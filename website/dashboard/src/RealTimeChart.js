import React, { useRef, useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import axios from 'axios';
import {
    Chart, CategoryScale, LinearScale, PointElement, LineElement, TimeScale,
    Title, Tooltip, Legend
} from 'chart.js';
import 'chartjs-adapter-date-fns'; 
import './Dashboard.css';
// Register the necessary components for Chart.js
Chart.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    TimeScale,
    Title,
    Tooltip,
    Legend
);

function Dashboard() {
    const [chartData, setChartData] = useState({
        flowCount: [],
        totalPackets: [],
        totalBytes: [],
        labels: []
    });

    useEffect(() => {
        const fetchData = () => {
            axios.get(`http://localhost:5000/api/flow_stats`)
                .then(response => {
                    const { flow_count, total_packets, total_bytes } = response.data;
                    setChartData(prevData => ({
                        flowCount: [...prevData.flowCount, flow_count],
                        totalPackets: [...prevData.totalPackets, total_packets],
                        totalBytes: [...prevData.totalBytes, total_bytes],
                        labels: [...prevData.labels, new Date().toISOString()]
                    }));
                })
                .catch(error => console.error('Error fetching data:', error));
        };

        const interval = setInterval(fetchData, 3000);
        return () => clearInterval(interval);
    }, []);

    // Expand function
    const expandChart = (chartId) => {
        const modal = document.getElementById(`modal-${chartId}`);
        const overlay = document.getElementById('overlay');
        modal.style.display = 'block';
        overlay.style.display = 'block';
        overlay.onclick = () => {
            modal.style.display = 'none';
            overlay.style.display = 'none';
        }
    }

    const renderChart = (data, label, chartId) => (
        <div className="chart-container" onClick={() => expandChart(chartId)}>
            <Line data={{
                labels: chartData.labels,
                datasets: [{
                    label: label,
                    data: data,
                    borderColor: chartId === 'flowCount' ? 'rgb(255,99,132)' : chartId === 'totalPackets' ? 'rgb(54, 162, 235)' : 'rgb(75, 192, 192)'
                }]
            }} options={{ scales: { x: { type: 'time', time: { unit: 'minute' } } } }} />
            <div id={`modal-${chartId}`} className="chart-modal">
                <Line data={{
                    labels: chartData.labels,
                    datasets: [{
                        label: label,
                        data: data,
                        borderColor: chartId === 'flowCount' ? 'rgb(255,99,132)' : chartId === 'totalPackets' ? 'rgb(54, 162, 235)' : 'rgb(75, 192, 192)'
                    }]
                }} options={{ scales: { x: { type: 'time', time: { tooltipFormat: 'DD MMM YYYY hh:mm:ss' } } } }} />
            </div>
        </div>
    );

    return (
        <div id="realTimeChart">
            <div className="dashboard">
                {renderChart(chartData.flowCount, 'Flow Count', 'flowCount')}
                {renderChart(chartData.totalPackets, 'Total Packets', 'totalPackets')}
                {renderChart(chartData.totalBytes, 'Total Bytes', 'totalBytes')}
            </div>
            <div id="overlay" className="overlay"></div>
        </div>
    );
}

export default Dashboard;
