import React from 'react'
import { Loader2 } from 'lucide-react'

const ProcessingStatus = ({ progress }) => {
    return (
        <div className="w-full text-center py-20 animate-fade-in">
            <div className="mb-8 relative w-32 h-32 mx-auto flex items-center justify-center">
                {/* Background Circle */}
                <div className="absolute inset-0 rounded-full border-4 border-gray-100"></div>
                {/* Progress Circle (Simple Rotation) */}
                <div
                    className="absolute inset-0 rounded-full border-4 border-black border-t-transparent animate-spin"
                ></div>
                <span className="text-2xl font-bold font-mono text-black">{progress}%</span>
            </div>

            <h3 className="text-2xl font-semibold text-gray-900 mb-3 tracking-tight">Processing Video...</h3>
            <p className="text-gray-500 text-sm max-w-sm mx-auto">
                Generating intermediate frames using RIFE AI model.
                This is a computationally intensive process.
            </p>
        </div>
    )
}

export default ProcessingStatus
