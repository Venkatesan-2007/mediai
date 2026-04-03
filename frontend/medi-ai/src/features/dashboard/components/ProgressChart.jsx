import React from 'react';

/**
 * ProgressChart Component
 * Displays a visual progress chart for the student dashboard
 * @param {number} progress - Overall progress percentage
 */
const ProgressChart = ({ progress }) => {
    // Mock data for weekly progress
    const weeklyData = [
        { day: 'Mon', value: 65 },
        { day: 'Tue', value: 72 },
        { day: 'Wed', value: 58 },
        { day: 'Thu', value: 80 },
        { day: 'Fri', value: 45 },
        { day: 'Sat', value: 90 },
        { day: 'Sun', value: progress }
    ];

    const maxValue = 100;

    return (
        <div className="w-full">
            {/* Circular Progress Indicator */}
            <div className="flex justify-center mb-6">
                <div className="relative w-32 h-32">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                        {/* Background circle */}
                        <circle
                            cx="50"
                            cy="50"
                            r="45"
                            fill="none"
                            stroke="#fce7f3"
                            strokeWidth="10"
                        />
                        {/* Progress circle */}
                        <circle
                            cx="50"
                            cy="50"
                            r="45"
                            fill="none"
                            stroke="url(#gradient)"
                            strokeWidth="10"
                            strokeLinecap="round"
                            strokeDasharray={`${(progress / 100) * 283} 283`}
                            className="transition-all duration-1000"
                        />
                        <defs>
                            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stopColor="#f472b6" />
                                <stop offset="100%" stopColor="#db2777" />
                            </linearGradient>
                        </defs>
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-3xl font-bold text-gray-800">{progress}%</span>
                    </div>
                </div>
            </div>

            {/* Weekly Bar Chart */}
            <div className="mt-6">
                <h4 className="text-gray-600 font-medium mb-4 text-center">Weekly Activity</h4>
                <div className="flex items-end justify-between h-32 gap-2">
                    {weeklyData.map((day, index) => (
                        <div key={index} className="flex flex-col items-center flex-1">
                            <div
                                className="w-full bg-gradient-to-t from-pink-400 to-pink-500 rounded-t-lg transition-all duration-300 hover:from-pink-500 hover:to-pink-600"
                                style={{ height: `${(day.value / maxValue) * 100}%` }}
                            ></div>
                            <span className="text-gray-500 text-xs mt-2">{day.day}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Stats Summary */}
            <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-pink-100">
                <div className="text-center">
                    <p className="text-2xl font-bold text-pink-600">42</p>
                    <p className="text-gray-500 text-xs">Topics Completed</p>
                </div>
                <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">156</p>
                    <p className="text-gray-500 text-xs">Questions Asked</p>
                </div>
                <div className="text-center">
                    <p className="text-2xl font-bold text-amber-600">12h</p>
                    <p className="text-gray-500 text-xs">Study Time</p>
                </div>
            </div>
        </div>
    );
};

export default ProgressChart;
