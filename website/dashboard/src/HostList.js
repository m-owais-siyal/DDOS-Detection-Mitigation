import React, { useEffect, useState } from 'react';
import { Table, Form, InputGroup, Button } from 'react-bootstrap';
import axios from 'axios';

function HostList () {
    const [hosts, setHosts] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchHosts = () => {
            axios.get('http://localhost:5000/api/hosts')
                .then(response => {
                    setHosts(response.data);
                })
                .catch(error => console.log(error));
        };
        fetchHosts();
    }, []);

    const handleSearch = (event) => {
        setSearchTerm(event.target.value.toLowerCase());
    };

    const filteredHosts = hosts.filter(host => host.name.toLowerCase().includes(searchTerm));

    return (
        <div>
            <InputGroup className="mb-3">
                <Form.Control
                    placeholder="Search by host name"
                    aria-label="Search by host name"
                    aria-describedby="basic-addon2"
                    onChange={handleSearch}
                />
                <InputGroup.Append>
                    <Button variant="outline-secondary">Search</Button>
                </InputGroup.Append>
            </InputGroup>
            <Table striped bordered hover>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Host Name</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {filteredHosts.map((host, index) => (
                        <tr key={index}>
                            <td>{index + 1}</td>
                            <td>{host.name}</td>
                            <td>{host.status}</td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </div>
    );
};

export default HostList
