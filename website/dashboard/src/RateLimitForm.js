import React, { useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import axios from 'axios';

function RateLimitForm () {
    const [macAddress, setMacAddress] = useState('');
    const [rateLimit, setRateLimit] = useState('');

    const handleSubmit = (event) => {
        event.preventDefault();
        axios.post('http://localhost:5000/set_rate_limit', { mac_address: macAddress, rate_limit: rateLimit })
            .then(response => alert('Rate limit set successfully!'))
            .catch(error => alert('Failed to set rate limit!'));
    };

    return (
        <Form onSubmit={handleSubmit}>
            <Form.Group controlId="formBasicEmail">
                <Form.Label>MAC Address</Form.Label>
                <Form.Control type="text" placeholder="Enter MAC address" value={macAddress} onChange={e => setMacAddress(e.target.value)} />
            </Form.Group>

            <Form.Group controlId="formBasicPassword">
                <Form.Label>Rate Limit</Form.Label>
                <Form.Control type="number" placeholder="Rate Limit" value={rateLimit} onChange={e => setRateLimit(e.target.value)} />
            </Form.Group>

            <Button variant="primary" type="submit">
                Submit
            </Button>
        </Form>
    );
};

export default RateLimitForm
