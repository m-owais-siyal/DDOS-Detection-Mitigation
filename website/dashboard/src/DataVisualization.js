import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Line, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, PieController, ArcElement, Title, Tooltip, Legend } from 'chart.js';
import { Form } from 'react-bootstrap';

// Register all necessary components for Chart.js
ChartJS.register(
  CategoryScale, LinearScale, BarElement, LineElement, PointElement, PieController, ArcElement,
  Title, Tooltip, Legend
);

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true
};

const DataVisualization = ({ selectedHeader }) => {
    const [chartData, setChartData] = useState({});
    const [chartType, setChartType] = useState('bar'); // Default to bar chart

    useEffect(() => {
        const fetchDataForChart = async () => {
            if (!selectedHeader) return;
            try {
                const response = await axios.get(`http://localhost:5000/api/data_visualization`, { params: { header: selectedHeader } });
                const counts = response.data; // Assumes response data is an object { value: count }
                setChartData({
                    labels: Object.keys(counts),
                    datasets: [{
                        label: `Count of ${selectedHeader}`,
                        data: Object.values(counts),
                        backgroundColor: Object.keys(counts).map(() => `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.5)`),
                        borderColor: Object.keys(counts).map(() => `rgb(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)})`),
                        borderWidth: 1,
                    }],
                });
            } catch (error) {
                console.error('Error fetching data for visualization:', error);
            }
        };

        fetchDataForChart();
    }, [selectedHeader]);

    // Function to render chart based on chartType
    const renderChart = () => {
        switch (chartType) {
            case 'line':
                return <Line data={chartData} options={chartOptions} />;
            case 'pie':
                return <Pie data={chartData} options={chartOptions} />;
            case 'bar':
            default:
                return <Bar data={chartData} options={chartOptions} />;
        }
    };

    return (
        <div style={{ width: '35%', margin: 'auto' }}>
            <Form.Select aria-label="Select Chart Type" onChange={e => setChartType(e.target.value)} value={chartType} className="mb-3">
                <option value="bar">Bar Chart</option>
                <option value="line">Line Chart</option>
                <option value="pie">Pie Chart</option>
                {/* Add more chart types as needed */}
            </Form.Select>
            
            {chartData.datasets && chartData.datasets.length > 0 ? renderChart() : <p>No data available for visualization.</p>}
        </div>
    );
};

export default DataVisualization;
