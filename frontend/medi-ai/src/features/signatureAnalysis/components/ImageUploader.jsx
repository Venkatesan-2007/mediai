import React, { useState, useRef } from 'react';

/**
 * ImageUploader Component
 * Handles image upload, preview, and validation for signature/prescription analysis
 * @param {function} onImageSelect - Callback when image is selected
 * @param {boolean} disabled - Whether uploader is disabled
 */
const ImageUploader = ({ onImageSelect, disabled = false }) => {
    const [dragActive, setDragActive] = useState(false);
    const [preview, setPreview] = useState(null);
    const [error, setError] = useState('');
    const inputRef = useRef(null);

    /**
     * Handle drag events
     * @param {object} e - Event object
     */
    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (disabled) return;

        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    /**
     * Handle drop event
     * @param {object} e - Event object
     */
    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (disabled) return;

        const files = e.dataTransfer.files;
        if (files && files[0]) {
            processFile(files[0]);
        }
    };

    /**
     * Handle file input change
     * @param {object} e - Event object
     */
    const handleChange = (e) => {
        const files = e.target.files;
        if (files && files[0]) {
            processFile(files[0]);
        }
    };

    /**
     * Process and validate file
     * @param {File} file - The file to process
     */
    const processFile = (file) => {
        setError('');

        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp'];
        if (!validTypes.includes(file.type)) {
            setError('Invalid file type. Please upload a JPG, PNG, or GIF image.');
            return;
        }

        // Validate file size (max 10MB)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            setError('File too large. Maximum size is 10MB.');
            return;
        }

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            setPreview(e.target.result);
            onImageSelect(file);
        };
        reader.readAsDataURL(file);
    };

    /**
     * Handle click on upload area
     */
    const handleClick = () => {
        if (!disabled) {
            inputRef.current.click();
        }
    };

    /**
     * Clear uploaded image
     */
    const clearImage = () => {
        setPreview(null);
        setError('');
        if (inputRef.current) {
            inputRef.current.value = '';
        }
        onImageSelect(null);
    };

    return (
        <div className="w-full">
            {/* Upload Area */}
            <div
                className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${dragActive
                        ? 'border-pink-500 bg-pink-50'
                        : preview
                            ? 'border-pink-300 bg-pink-50/50'
                            : 'border-pink-200 hover:border-pink-400 bg-white/50'
                    } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={handleClick}
            >
                <input
                    ref={inputRef}
                    type="file"
                    accept="image/jpeg,image/jpg,image/png,image/gif,image/bmp"
                    onChange={handleChange}
                    className="hidden"
                    disabled={disabled}
                />

                {preview ? (
                    <div className="relative">
                        <img
                            src={preview}
                            alt="Preview"
                            className="max-h-64 mx-auto rounded-xl shadow-soft"
                        />
                        <button
                            type="button"
                            onClick={(e) => {
                                e.stopPropagation();
                                clearImage();
                            }}
                            className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors shadow-lg"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                ) : (
                    <div className="py-8">
                        <div className="w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg className="w-8 h-8 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <p className="text-gray-600 font-medium mb-2">
                            Drag and drop your image here
                        </p>
                        <p className="text-gray-400 text-sm">
                            or click to browse
                        </p>
                        <p className="text-gray-400 text-xs mt-4">
                            Supported formats: JPG, PNG, GIF (Max 10MB)
                        </p>
                    </div>
                )}
            </div>

            {/* Error Message */}
            {error && (
                <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm flex items-center">
                    <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {error}
                </div>
            )}
        </div>
    );
};

export default ImageUploader;
