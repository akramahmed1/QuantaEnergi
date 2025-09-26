import React from 'react';

const LogisticsForm = () => {
  const [data, setData] = React.useState({location: '', volume: 0});
  
  return (
    <form>
      <input 
        placeholder='Location' 
        onChange={e => setData({...data, location: e.target.value})} 
      />
      <input 
        type='number' 
        placeholder='Volume' 
        onChange={e => setData({...data, volume: parseFloat(e.target.value)})} 
      />
    </form>
  );
};

export default LogisticsForm;
