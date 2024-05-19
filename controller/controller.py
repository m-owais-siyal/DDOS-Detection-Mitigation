import os
from ryu.controller import ofp_event,event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
import switchm
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib
import requests
import ipaddress


class SetThresholdMessage(event.EventBase):
    def __init__(self, threshold):
        super(SetThresholdMessage, self).__init__()
        self.rate_limit = None
        

class SimpleMonitor13(switchm.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.rate_limit = None
        self.alert_active = False
        self.alert_message = ""
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        scaler_path = os.path.join(os.path.dirname(__file__), 'scaler.pkl')
        self.scaler = joblib.load(scaler_path) 
        flow_model_path = os.path.join(os.path.dirname(__file__), 'flow_model.pkl')
        self.flow_model = joblib.load(flow_model_path) 
        print("Controller started sucessfully ")
        
    def get_flow_stats(self):
        total_packets = 0
        total_bytes = 0
        unique_flow_ids = set()

        basedir = os.path.abspath(os.path.dirname(__file__))
        csv_file_path = os.path.join(basedir, '../Terminal/flask/PredictFlowStatsfile.csv')

        #current_dir = os.path.dirname(os.path.abspath(__file__))
        #csv_file_path = os.path.join(current_dir, 'PredictFlowStatsfile.csv')

        with open(csv_file_path, 'r') as file:
            next(file)
            for line in file:
                fields = line.split(',')
                flow_id = fields[1].strip()   #flow id is 3nd  (-1 when writting index)  *********  IMP if dataset is changed
                byte_count = int(fields[12])  #flow id is 17th (-1 when writting index)  *********  IMP if dataset is changed
                if flow_id:
                    total_packets += 1
                    total_bytes += byte_count
                    if flow_id not in unique_flow_ids:
                        unique_flow_ids.add(flow_id)
        flow_stats = {"flow_count": len(unique_flow_ids) , "total_packets": total_packets, "total_bytes": total_bytes}
        return flow_stats

    def get_switch_stats(self):
        switch_stats = {"switch_count": 5, "active_switches": 3}
        return switch_stats
    
    def get_ddos_alert(self):
        print("in the get_ddos_alert finction : ", self.alert_message)
        return {'alert': self.alert_active, 'message': self.alert_message}
    
    def send_alert_status(self, alert_active, message):
        url = 'http://localhost:5000/api/update_alert'
        data = {'alert': alert_active, 'message': message}
        requests.post(url, json=data)

    def set_rate_limit(self, threshold):
        self.rate_limit = threshold
    


   

    

    def create_flow_stats(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        all_flow_stats_file_path = os.path.join(current_dir, 'AllFlowStatsfile.csv')
        #predict_flow_stats_file_path = os.path.join(current_dir, 'PredictFlowStatsfile.csv')
        predict_flow_stats_file_path = os.path.join(current_dir, '../Terminal/flask/PredictFlowStatsfile.csv')

        file1 = open(all_flow_stats_file_path, "a+")

        file1.seek(0, 2)  
        file_size = file1.tell()  

        if file_size == 0:
            file1.write('timestamp,flow_id,ip_src,tp_src,ip_dst,tp_dst,ip_proto,flow_duration_sec,flow_duration_nsec,idle_timeout,hard_timeout,packet_count,byte_count,packet_count_per_second,packet_count_per_nsecond,Label\n')
        file1.close()
        file0 = open(predict_flow_stats_file_path, "r")
        next(file0)
        file1 = open(all_flow_stats_file_path, "a+")
        for line in file0:
            
            file1.write(line)
        file0.close()
        file1.close()


    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)

            self.flow_predict()

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):

        timestamp = datetime.now()
        timestamp = timestamp.timestamp()

        file0 = open("PredictFlowStatsfile.csv","w")
        file0.write('timestamp,flow_id,ip_src,tp_src,ip_dst,tp_dst,ip_proto,flow_duration_sec,flow_duration_nsec,idle_timeout,hard_timeout,packet_count,byte_count,packet_count_per_second,packet_count_per_nsecond\n')
        body = ev.msg.body
        icmp_code = -1
        icmp_type = -1
        tp_src = 0
        tp_dst = 0

        for stat in sorted([flow for flow in body if (flow.priority == 1)], key=lambda flow: (flow.match['eth_type'], flow.match['ipv4_src'], flow.match['ipv4_dst'], flow.match['ip_proto'])):
            ip_src = stat.match['ipv4_src']
            ip_dst = stat.match['ipv4_dst']
            ip_proto = stat.match['ip_proto']
            
            if stat.match['ip_proto'] == 1:
                icmp_code = stat.match['icmpv4_code']
                icmp_type = stat.match['icmpv4_type']
                
            elif stat.match['ip_proto'] == 6:
                tp_src = stat.match['tcp_src']
                tp_dst = stat.match['tcp_dst']

            elif stat.match['ip_proto'] == 17:
                tp_src = stat.match['udp_src']
                tp_dst = stat.match['udp_dst']

            flow_id = str(ip_src) + str(tp_src) + str(ip_dst) + str(tp_dst) + str(ip_proto)
          
            try:
                packet_count_per_second = stat.packet_count/stat.duration_sec
                packet_count_per_nsecond = stat.packet_count/stat.duration_nsec
            except:
                packet_count_per_second = 0
                packet_count_per_nsecond = 0
                
            try:
                byte_count_per_second = stat.byte_count/stat.duration_sec
                byte_count_per_nsecond = stat.byte_count/stat.duration_nsec
            except:
                byte_count_per_second = 0
                byte_count_per_nsecond = 0
                
            file0.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n"
                .format(timestamp, flow_id, ip_src, tp_src,ip_dst, tp_dst,
                        stat.match['ip_proto'], stat.duration_sec, stat.duration_nsec,
                        stat.idle_timeout, stat.hard_timeout,
                        stat.packet_count,stat.byte_count,
                        packet_count_per_second,packet_count_per_nsecond))

            
        file0.close()


    


    def flow_predict(self):
        try:
            predict_flow_dataset = pd.read_csv('PredictFlowStatsfile.csv')

            original_flow_id = predict_flow_dataset['flow_id'].copy()
            original_ips_src = predict_flow_dataset['ip_src'].copy()
            original_ips_dst = predict_flow_dataset['ip_dst'].copy()
          
                        
            predict_flow_dataset['flow_id'] = predict_flow_dataset['flow_id'].str.replace('.', '')
            predict_flow_dataset['ip_src'] = predict_flow_dataset['ip_src'].str.replace('.', '')
            predict_flow_dataset['ip_dst'] = predict_flow_dataset['ip_dst'].str.replace('.', '')



            X_predict_flow = predict_flow_dataset.iloc[:, :].values
            X_predict_flow = X_predict_flow.astype('float64') 
            X_predict_flow = self.scaler.transform(X_predict_flow)
            y_flow_pred = self.flow_model.predict(X_predict_flow)
            predict_flow_dataset['Label'] = y_flow_pred

            

            legitimate_trafic = 0
            ddos_trafic = 0

            for i in y_flow_pred:
                if i == 0:
                    legitimate_trafic = legitimate_trafic + 1
                else:
                    ddos_trafic = ddos_trafic + 1
                    victim = int(predict_flow_dataset.iloc[i, 4]) % 20

            print("------------------------------------------------------------------------------")
            if (legitimate_trafic / len(y_flow_pred) * 100) > 80:
                self.alert_active = False
                print("Traffic is Legitimate!")
            else:
                print("NOTICE!! DoS Attack in Progress!!!")
                print("Victim Host: h{}".format(victim))
                self.alert_active = True
                self.alert_message = "NOTICE!! DoS Attack in Progress on Host h{}!".format(victim)
                self.send_alert_status(self.alert_active,self.alert_message)
                print("Mitigation process in progress!")
                self.mitigation = 1  

            print("------------------------------------------------------------------------------")
            
            predict_flow_dataset['flow_id'] = original_flow_id
            predict_flow_dataset['ip_src'] = original_ips_src
            predict_flow_dataset['ip_dst'] = original_ips_dst

            predict_flow_dataset.to_csv('PredictFlowStatsfile.csv', index=False)

            self.create_flow_stats()
            
            file0 = open("PredictFlowStatsfile.csv","w")
            file0.write('timestamp,flow_id,ip_src,tp_src,ip_dst,tp_dst,ip_proto,flow_duration_sec,flow_duration_nsec,idle_timeout,hard_timeout,packet_count,byte_count,packet_count_per_second,packet_count_per_nsecond\n')
            file0.close()

        except Exception as e:
            #print("Error:", e)     #printing the error message
            pass

