import React, { useState } from 'react';
const GamifiedHub = () => {
  const [feedback, setFeedback] = useState("");
  const [rating, setRating] = useState(0);
  const [leaderboard, setLeaderboard] = useState([{ name: "Trader1", profit: 1000 }]);
  const [badges, setBadges] = useState(["Fast Resolver"]);
  const [points, setPoints] = useState(0);
  const submitFeedback = () => {
    fetch('http://localhost:8000/api/audit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback })
    }).then(() => { setPoints(points + 10); alert('Feedback submitted, +10 points'); });
    fetch('http://localhost:8000/api/gamify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'feedback' })
    });
  };
  return (
    <div>
      <h3>Most Profitable Trades</h3>
      {leaderboard.map((trader, i) => <p key={i}>{trader.name}: {trader.profit} credits</p>)}
      <h3>Engineer Badges</h3>
      {badges.map((badge, i) => <p key={i}>{badge}</p>)}
      <input type="number" min="1" max="5" value={rating} onChange={e => setRating(e.target.value)} />
      {"".repeat(rating)} 
      <input value={feedback} onChange={e => setFeedback(e.target.value)} />
      <button onClick={submitFeedback}>Submit</button>
      Gamified Mode - Points: {points}
    </div>
  );
};
export default GamifiedHub;
