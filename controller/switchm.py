from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, arp, ethernet, ether_types, ipv4, icmp, tcp, udp
from ryu.lib.packet import in_proto

FLOW_SERIAL_NO = 0

def get_flow_number():
    global FLOW_SERIAL_NO
    FLOW_SERIAL_NO = FLOW_SERIAL_NO + 1
    return FLOW_SERIAL_NO

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.mitigation = 0
        self.arp_ip_to_port = {}
        self.threshold = 1000  # Default threshold value
        self.bucket = 0  # Initialize bucket with threshold value

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        flow_serial_no = get_flow_number()
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions, flow_serial_no)

    def add_flow(self, datapath, priority, match, actions, serial_no, buffer_id=None, idle=0, hard=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, cookie=serial_no, buffer_id=buffer_id,
                                    idle_timeout=idle, hard_timeout=hard,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, cookie=serial_no, priority=priority,
                                    idle_timeout=idle, hard_timeout=hard,
                                    match=match, instructions=inst)
            
        datapath.send_msg(mod)

    def block_port(self, datapath, portnumber):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(in_port=portnumber)
        actions = []
        flow_serial_no = get_flow_number()
        self.add_flow(datapath, 100, match, actions, flow_serial_no, hard=120)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        # Update bucket
        self.bucket += 1  # Add token at constant rate
        #if self.bucket > self.threshold:
            #self.bucket = self.threshold  # Limit bucket to threshold

        if 2>1:#if self.bucket < self.threshold:
            # If there are enough tokens in the bucket, process the packet
            pkt = packet.Packet(msg.data)
            eth = pkt.get_protocols(ethernet.ethernet)[0]
            dst = eth.dst
            src = eth.src

            dpid = datapath.id
            self.mac_to_port.setdefault(dpid, {})
            self.arp_ip_to_port.setdefault(dpid, {})
            self.arp_ip_to_port[dpid].setdefault(in_port, [])

            # learn a mac address to avoid FLOOD next time.
            self.mac_to_port[dpid][src] = in_port

            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
            else:
                out_port = ofproto.OFPP_FLOOD

            actions = [parser.OFPActionOutput(out_port)]
            #if ARP Request packet , log the IP and MAC Address from that port
            if eth.ethertype == ether_types.ETH_TYPE_ARP:
                #self.logger.info("Received ARP Packet %s %s %s ", dpid, src, dst)
                a = pkt.get_protocol(arp.arp)
                #print "arp packet ", a
                if a.opcode == arp.ARP_REQUEST or a.opcode == arp.ARP_REPLY:
                    if not a.src_ip in self.arp_ip_to_port[dpid][in_port]:
                        self.arp_ip_to_port[dpid][in_port].append(a.src_ip)

            # install a flow to avoid packet_in next time
            if out_port != ofproto.OFPP_FLOOD:

                # check IP Protocol and create a match for IP
                if eth.ethertype == ether_types.ETH_TYPE_IP:
                    ip = pkt.get_protocol(ipv4.ipv4)
                    srcip = ip.src
                    dstip = ip.dst
                    protocol = ip.proto

                    # if ICMP Protocol
                    if protocol == in_proto.IPPROTO_ICMP:
                        t = pkt.get_protocol(icmp.icmp)
                        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                                ipv4_src=srcip, ipv4_dst=dstip,
                                                ip_proto=protocol,icmpv4_code=t.code,
                                                icmpv4_type=t.type)

                    #  if TCP Protocol
                    elif protocol == in_proto.IPPROTO_TCP:
                        t = pkt.get_protocol(tcp.tcp)
                        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                                ipv4_src=srcip, ipv4_dst=dstip,
                                                ip_proto=protocol,
                                                tcp_src=t.src_port, tcp_dst=t.dst_port,)

                    #  If UDP Protocol
                    elif protocol == in_proto.IPPROTO_UDP:
                        u = pkt.get_protocol(udp.udp)
                        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                                ipv4_src=srcip, ipv4_dst=dstip,
                                                ip_proto=protocol,
                                                udp_src=u.src_port, udp_dst=u.dst_port,)

                    if self.mitigation:
                        if not (srcip in self.arp_ip_to_port[dpid][in_port]):
                            print("Attack detected from port ", in_port)
                            print("Blocking port ", in_port)
                            self.block_port(datapath, in_port)
                            self.mitigation = 0
                            return

                    flow_serial_no = get_flow_number()
                    if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                        self.add_flow(datapath, 1, match, actions, flow_serial_no, msg.buffer_id, idle=20, hard=100)
                        return
                    else:
                        self.add_flow(datapath, 1, match, actions, flow_serial_no, idle=20, hard=100)
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)
            # Consume token
            self.bucket -= 1
        #else:
            # If there are not enough tokens, drop the packet
            #self.logger.info("Packet dropped due to rate limiting")
