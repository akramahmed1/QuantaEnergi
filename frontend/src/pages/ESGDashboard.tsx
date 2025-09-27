import { BarChart, Bar } from 'recharts';

const data = [{name: 'CO2', value: 50}];

export default function ESGDashboard() {
  return (
    <BarChart width={400} height={300} data={data}>
      <Bar dataKey="value" fill="#8884d8" />
    </BarChart>
  );
}
