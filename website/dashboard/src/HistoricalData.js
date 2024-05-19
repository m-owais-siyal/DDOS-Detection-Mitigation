import React, { useState, useEffect, useCallback } from 'react';
import { Form, InputGroup, Button } from 'react-bootstrap';
import axios from 'axios';
import { FixedSizeList as List } from 'react-window';

// Constants for style adjustments
const MIN_WIDTHS = {
  'timestamp': '200px',
  'flow_id': '200px',
  'default': '100px',
};

const MAX_WIDTHS = {
  'packet_count': '50px',
  'byte_count': '50px',
  'Label': '50px',
  'packet_count_per_nsecond': '50px',
  'packet_count_per_second': '50px',
  'default': 'auto',
};

const columnOrder = [
  'timestamp', 'flow_id', 'ip_src', 'tp_src', 'ip_dst',
  'tp_dst', 'ip_proto', 'flow_duration_sec', 'flow_duration_nsec',
  'idle_timeout', 'hard_timeout', 'packet_count', 'byte_count',
  'packet_count_per_second', 'packet_count_per_nsecond','Label'
];

const customDisplayNames = {
  'ip_src': 'Source IP',
  'ip_dst': 'Dest IP',
  'tp_src': 'Source Port',
  'tp_dst': 'Dest Port',
  'packet_count_per_second' : 'Packets/sec',
  'packet_count_per_nsecond' : 'Packets/nec',
  'flow_duration_sec' : 'Flow/sec',
  'flow_duration_nsec' : 'Flow/nsec'
};

const headerStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  background: '#eee',
  padding: '10px 0',
  flexWrap: 'wrap',
};

// Dynamic style for cell based on content length
const cellStyle = (key, idx) => {
  const minWidth = MIN_WIDTHS[key] || MIN_WIDTHS['default'];
  const maxWidth = MAX_WIDTHS[key] || MAX_WIDTHS['default'];
  return {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flex: idx === columnOrder.length - 1 ? 'none' : '1',
    padding: '10px',
    borderRight: idx === columnOrder.length - 1 ? 'none' : '1px solid #ddd',
    boxSizing: 'border-box',
    minWidth: minWidth,
    maxWidth: maxWidth,
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  };
};

// Styles for header with dynamic font size based on text length
const headerCellStyle = (displayName) => ({
  ...cellStyle(displayName.toLowerCase().replace(/\s+/g, '_'), 0), // Reuse cellStyle for consistent styling
  fontSize: displayName.length > 10 ? '0.85em' : '1em',
  fontWeight: 'bold',
});

const Row = ({ index, style, data }) => {
  const item = data[index];
  return (
    <div style={{ ...style, display: 'flex' }}>
      {columnOrder.map((key, idx) => {
        const value = item && item[key] !== undefined ? item[key].toString() : '-';
        return (
          <div
            key={key}
            style={cellStyle(key, idx)}
            title={value}
          >
            {value}
          </div>
        );
      })}
    </div>
  );
};

function HistoricalData() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/api/historical_data', {
        params: {
          page,
          per_page: 30,
          search: searchTerm,
          sort_order: sortOrder,
        },
      });

      if (Array.isArray(response.data)) {
        const newData = response.data.map(item => {
          return columnOrder.reduce((acc, key) => ({
            ...acc,
            [key]: item[key] !== null ? item[key] : '0', // Ensure zeros are displayed
          }), {});
        });
        setData(prevData => [...prevData, ...newData]);
        setPage(prevPage => prevPage + 1);
        setHasMore(response.data.length >= 30); // Assume there's no more data if less than 30 items were returned
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setHasMore(false);
    }
    setLoading(false);
  }, [page, searchTerm, sortOrder]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleSearch = () => {
    setData([]);
    setPage(1);
    setHasMore(true);
    fetchData();
  };

  const toggleSortOrder = () => {
    setSortOrder(prevSortOrder => prevSortOrder === 'asc' ? 'desc' : 'asc');
    setData([]);
    setPage(1);
    setHasMore(true);
    fetchData();
  };

  const renderHeader = () => (
    <div style={headerStyle}>
      {columnOrder.map((key, idx) => {
        const displayName = customDisplayNames[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        return (
          <div
            key={key}
            style={headerCellStyle(displayName)}
          >
            {displayName}
          </div>
        );
      })}
    </div>
  );

  return (
    <div id="historicalData">
      <InputGroup className="mb-3">
        <Form.Control
          placeholder="Enter Query"
          onChange={handleSearchChange}
          value={searchTerm}
        />
        <Button variant="outline-secondary" onClick={handleSearch}>Search</Button>
        <Button variant="outline-secondary" onClick={toggleSortOrder}>Toggle Sort</Button>
      </InputGroup>
      {renderHeader()}
      <List
        height={400}
        itemCount={data.length}
        itemSize={50}
        width={'100%'}
        itemData={data}
      >
        {Row}
      </List>
      {loading && <div>Loading more items...</div>}
      {!hasMore && <div>No more data to load.</div>}
    </div>
  );
}

export default HistoricalData;
