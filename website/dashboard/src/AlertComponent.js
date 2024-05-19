import React, { useEffect, useState } from 'react';
import { Alert } from 'react-bootstrap';
import axios from 'axios';
import './Dashboard.css';

function AlertComponent() {
    const [alertInfo, setAlertInfo] = useState({ show: false, message: '' });

    useEffect(() => {
        const checkForAlerts = () => {
            axios.get('http://localhost:5000/api/ddos_alert')
                .then(response => {
                    if (response.data.alert) {
                        setAlertInfo({ show: true, message: response.data.message });
                    } else {
                        setAlertInfo(prev => ({ ...prev, show: false }));
                    }
                })
                .catch(error => console.log(error));
        };

        const interval = setInterval(checkForAlerts, 500);
        return () => clearInterval(interval);
    }, []);

    const handleClose = () => {
        axios.post('http://localhost:5000/api/update_alert1', { alert: false, message: '' })
            .then(() => {
                setAlertInfo({ show: false, message: '' });
            })
            .catch(error => console.log(error));
    };

    return (
        alertInfo.show && (
            <Alert variant="danger" className="alert-fixed-top" dismissible onClose={handleClose} transition={true}>
                {alertInfo.message}
            </Alert>
        )
    );
}

export default AlertComponent;