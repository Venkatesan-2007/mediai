import React from 'react';

/**
 * DashboardCards Component
 * Displays key metrics cards for the student dashboard
 * @param {number} progress - Overall progress percentage
 * @param {number} questionsToday - Number of questions asked today
 * @param {Array} upcomingExams - Array of upcoming exams
 */
const DashboardCards = ({ progress, questionsToday, upcomingExams }) => {
    // Find nearest exam
    const nearestExam = upcomingExams.reduce((nearest, exam) => {
        return exam.daysLeft < nearest.daysLeft ? exam : nearest;
    }, upcomingExams[0]);

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Progress Card */}
            <div className="card-soft p-5 animate-slide-in">
                <div className="flex items-center justify-between mb-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-pink-400 to-pink-600 rounded-xl flex items-center justify-center shadow-soft">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                    </div>
                    <span className="text-3xl font-bold text-pink-600">{progress}%</span>
                </div>
                <h3 className="text-gray-600 font-medium">Overall Progress</h3>
                <div className="w-full bg-pink-100 rounded-full h-2 mt-2">
                    <div
                        className="bg-gradient-to-r from-pink-400 to-pink-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${progress}%` }}
                    ></div>
                </div>
            </div>

            {/* Questions Today Card */}
            <div className="card-soft p-5 animate-slide-in delay-100">
                <div className="flex items-center justify-between mb-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-purple-600 rounded-xl flex items-center justify-center shadow-soft">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <span className="text-3xl font-bold text-purple-600">{questionsToday}</span>
                </div>
                <h3 className="text-gray-600 font-medium">Questions Today</h3>
                <p className="text-gray-400 text-sm mt-1">Keep learning!</p>
            </div>

            {/* Upcoming Exams Card */}
            <div className="card-soft p-5 animate-slide-in delay-200">
                <div className="flex items-center justify-between mb-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center shadow-soft">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                        </svg>
                    </div>
                    <span className="text-3xl font-bold text-amber-600">{upcomingExams.length}</span>
                </div>
                <h3 className="text-gray-600 font-medium">Upcoming Exams</h3>
                {nearestExam && (
                    <p className="text-amber-500 text-sm mt-1">
                        📅 {nearestExam.name} in {nearestExam.daysLeft} days
                    </p>
                )}
            </div>

            {/* Study Streak Card */}
            <div className="card-soft p-5 animate-slide-in delay-300">
                <div className="flex items-center justify-between mb-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-teal-500 rounded-xl flex items-center justify-center shadow-soft">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
                        </svg>
                    </div>
                    <span className="text-3xl font-bold text-green-600">7</span>
                </div>
                <h3 className="text-gray-600 font-medium">Day Streak</h3>
                <p className="text-green-500 text-sm mt-1">🔥 Keep it up!</p>
            </div>
        </div>
    );
};

export default DashboardCards;
