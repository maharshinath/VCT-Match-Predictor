import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const TeamStatsDashboard = ({team1, team2, matchupData}) => {
  // Original data
  const rawData = {
    "Team A Winrate vs B": matchupData["Team A Winrate vs B"],
    "Team A Winrate": team1["Winrate"],
    "Team A K/D Ratio": team1["K/D Ratio"],
    "Team A Average Damage": team1["Average Damage"],
    "Team A Average Combat Score": team1["Average Combat Score"],
    "Team A Average First Kills": team1["Average First Kills"],
    "Team B Winrate vs A": matchupData["Team B Winrate vs A"],
    "Team B Winrate": team2["Winrate"],
    "Team B K/D Ratio": team2["K/D Ratio"],
    "Team B Average Damage": team2["Average Damage"],
    "Team B Average Combat Score": team2["Average Combat Score"],
    "Team B Average First Kills": team2["Average First Kills"]
  };

  // Data for bar chart (excluding head-to-head stats)
  const barData = [
    {
      stat: 'Overall Winrate (%)',
      'Team A': rawData["Team A Winrate"],
      'Team B': rawData["Team B Winrate"]
    },
    {
      stat: 'K/D Ratio',
      'Team A': rawData["Team A K/D Ratio"],
      'Team B': rawData["Team B K/D Ratio"]
    },
    {
      stat: 'Average Damage',
      'Team A': rawData["Team A Average Damage"],
      'Team B': rawData["Team B Average Damage"]
    },
    {
      stat: 'Average Combat Score',
      'Team A': rawData["Team A Average Combat Score"],
      'Team B': rawData["Team B Average Combat Score"]
    },
    {
      stat: 'Average First Kills',
      'Team A': rawData["Team A Average First Kills"],
      'Team B': rawData["Team B Average First Kills"]
    }
  ];


  return (
    <div className="w-full max-w-7xl mx-auto p-6 bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Team Performance Dashboard</h1>
        <p className="text-gray-600">Comprehensive analysis of {team1["Team"]} vs {team2["Team"]} statistics</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Bar Chart Section */}
        <div className="xl:col-span-2">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">Overall Performance Comparison</h2>
            <ResponsiveContainer width="100%" height={500}>
              <BarChart
                data={barData}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="stat" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#f8f9fa', 
                    border: '1px solid #dee2e6',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Bar 
                  dataKey="Team A" 
                  fill="#3B82F6" 
                  radius={[4, 4, 0, 0]}
                  name={team1["Team"]}
                />
                <Bar 
                  dataKey="Team B" 
                  fill="#EF4444" 
                  radius={[4, 4, 0, 0]}
                  name={team2["Team"]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        
        
      

      {/* Stats Summary Table */}
      <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">Detailed Statistics</h2>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-50">
                <th className="text-left p-3 border-b-2 border-gray-200 font-semibold text-gray-700">Metric</th>
                <th className="text-center p-3 border-b-2 border-gray-200 font-semibold text-blue-600">{team1["Team"]}
                </th>
                <th className="text-center p-3 border-b-2 border-gray-200 font-semibold text-red-600">{team2["Team"]}</th>
                <th className="text-center p-3 border-b-2 border-gray-200 font-semibold text-gray-700">Difference</th>
              </tr>
            </thead>
            <tbody>
              <tr className="hover:bg-gray-50">
                <td className="p-3 border-b border-gray-200">Overall Winrate (%)</td>
                <td className="p-3 border-b border-gray-200 text-center">{rawData["Team A Winrate"].toFixed(1)}%</td>
                <td className="p-3 border-b border-gray-200 text-center">{rawData["Team B Winrate"].toFixed(1)}%</td>
                <td className="p-3 border-b border-gray-200 text-center">
                  {(rawData["Team B Winrate"] - rawData["Team A Winrate"]).toFixed(1)}%
                </td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="p-3 border-b border-gray-200">K/D Ratio</td>
                <td className="p-3 border-b border-gray-200 text-center">{rawData["Team A K/D Ratio"].toFixed(3)}</td>
                <td className="p-3 border-b border-gray-200 text-center">{rawData["Team B K/D Ratio"].toFixed(3)}</td>
                <td className="p-3 border-b border-gray-200 text-center">
                  {(rawData["Team B K/D Ratio"] - rawData["Team A K/D Ratio"]).toFixed(3)}
                </td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="p-3 border-b border-gray-200">Average Damage</td>
                <td className="p-3 border-b border-gray-200 text-center">{rawData["Team A Average Damage"].toFixed(1)}</td>
                <td className="p-3 border-b border-gray-200 text-center">{rawData["Team B Average Damage"].toFixed(1)}</td>
                <td className="p-3 border-b border-gray-200 text-center">
                  {(rawData["Team B Average Damage"] - rawData["Team A Average Damage"]).toFixed(1)}
                </td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="p-3 border-b border-gray-200">Average Combat Score</td>
                <td className="p-3 border-b border-gray-200 text-center">{rawData["Team A Average Combat Score"].toFixed(1)}</td>
                <td className="p-3 border-b border-gray-200 text-center">{rawData["Team B Average Combat Score"].toFixed(1)}</td>
                <td className="p-3 border-b border-gray-200 text-center">
                  {(rawData["Team B Average Combat Score"] - rawData["Team A Average Combat Score"]).toFixed(1)}
                </td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="p-3 border-b border-gray-200">Average First Kills</td>
                <td className="p-3 border-b border-gray-200 text-center">{rawData["Team A Average First Kills"].toFixed(2)}</td>
                <td className="p-3 border-b border-gray-200 text-center">{rawData["Team B Average First Kills"].toFixed(2)}</td>
                <td className="p-3 border-b border-gray-200 text-center">
                  {(rawData["Team B Average First Kills"] - rawData["Team A Average First Kills"]).toFixed(2)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    </div>
    
  );
};

export default TeamStatsDashboard;