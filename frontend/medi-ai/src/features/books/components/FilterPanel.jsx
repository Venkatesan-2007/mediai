import React from 'react';

/**
 * FilterPanel Component
 * Filter options for year of study, book type (Core/Reference), and subject
 * @param {Object} filters - Current filter state
 * @param {Function} onFilterChange - Handler for filter changes
 */
const FilterPanel = ({ filters, onFilterChange }) => {
    const yearOptions = ['All Years', '1st Year', '2nd Year', '3rd Year', '4th Year', '5th Year'];
    const typeOptions = ['All Types', 'Core', 'Reference'];
    const subjectOptions = [
        'All Subjects',
        'Anatomy',
        'Physiology',
        'Biochemistry',
        'Pharmacology',
        'Pathology',
        'Microbiology',
        'Medicine',
        'Surgery',
        'Obstetrics & Gynecology',
        'Pediatrics',
        'Psychiatry',
        'Dermatology',
        'Radiology'
    ];

    return (
        <div className="bg-white rounded-xl border border-gray-100 p-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-800">Filters</h3>
                <button
                    onClick={() => onFilterChange({ year: 'All Years', type: 'All Types', subject: 'All Subjects' })}
                    className="text-sm text-gray-500 hover:text-gray-700"
                >
                    Clear All
                </button>
            </div>

            <div className="space-y-4">
                {/* Year of Study */}
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-2">
                        Year of Study
                    </label>
                    <select
                        value={filters.year}
                        onChange={(e) => onFilterChange({ ...filters, year: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:border-gray-400 focus:outline-none text-sm bg-white"
                    >
                        {yearOptions.map((year) => (
                            <option key={year} value={year}>{year}</option>
                        ))}
                    </select>
                </div>

                {/* Book Type */}
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-2">
                        Book Type
                    </label>
                    <div className="flex gap-2">
                        {typeOptions.map((type) => (
                            <button
                                key={type}
                                onClick={() => onFilterChange({ ...filters, type })}
                                className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${filters.type === type
                                        ? 'bg-gray-800 text-white'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                            >
                                {type}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Subject */}
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-2">
                        Subject
                    </label>
                    <select
                        value={filters.subject}
                        onChange={(e) => onFilterChange({ ...filters, subject: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:border-gray-400 focus:outline-none text-sm bg-white"
                    >
                        {subjectOptions.map((subject) => (
                            <option key={subject} value={subject}>{subject}</option>
                        ))}
                    </select>
                </div>
            </div>
        </div>
    );
};

export default FilterPanel;
