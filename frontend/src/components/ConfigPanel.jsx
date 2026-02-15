import React, { useState } from 'react'
import { Play, ArrowLeft, Zap, Eye } from 'lucide-react'

const ConfigPanel = ({ metadata, onStart, onBack }) => {
    const [multiplier, setMultiplier] = useState(2);
    const [visualization, setVisualization] = useState('none'); // 'none', 'flow'

    const handleStart = () => {
        onStart(multiplier, visualization);
    };

    return (
        <div className="w-full animate-fade-in">
            <button
                onClick={onBack}
                className="mb-8 text-sm text-gray-500 hover:text-black flex items-center gap-2 transition-colors"
            >
                <ArrowLeft className="w-4 h-4" />
                Back to Upload
            </button>

            <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="p-4 border border-gray-100 rounded-lg bg-gray-50">
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">FPS</p>
                    <p className="text-2xl font-mono font-medium text-gray-900">{metadata.fps.toFixed(2)}</p>
                </div>
                <div className="p-4 border border-gray-100 rounded-lg bg-gray-50">
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Duration</p>
                    <p className="text-2xl font-mono font-medium text-gray-900">{metadata.duration.toFixed(1)}s</p>
                </div>
            </div>

            {/* Target FPS Section */}
            <div className="mb-8">
                <label className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-4">
                    <Zap className="w-4 h-4" />
                    Target Speed
                </label>
                <div className="grid grid-cols-2 gap-4">
                    <button
                        onClick={() => setMultiplier(2)}
                        className={`
              p-4 rounded-lg border text-left transition-all
              ${multiplier === 2
                                ? 'border-black bg-black text-white shadow-lg'
                                : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                            }
            `}
                    >
                        <div className="text-lg font-bold">2x</div>
                        <div className={`text-xs ${multiplier === 2 ? 'text-gray-400' : 'text-gray-500'}`}>
                            {(metadata.fps * 2).toFixed(2)} FPS
                        </div>
                    </button>

                    <button
                        onClick={() => setMultiplier(4)}
                        className={`
              p-4 rounded-lg border text-left transition-all
              ${multiplier === 4
                                ? 'border-black bg-black text-white shadow-lg'
                                : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                            }
            `}
                    >
                        <div className="text-lg font-bold">4x</div>
                        <div className={`text-xs ${multiplier === 4 ? 'text-gray-400' : 'text-gray-500'}`}>
                            {(metadata.fps * 4).toFixed(2)} FPS
                        </div>
                    </button>
                </div>
            </div>

            {/* Visualization Section */}
            <div className="mb-10">
                <label className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-4">
                    <Eye className="w-4 h-4" />
                    Visualization Mode
                </label>
                <div className="flex gap-4">
                    <label className={`
            flex-1 p-3 rounded-lg border cursor-pointer transition-all flex items-center justify-center gap-2
            ${visualization === 'none'
                            ? 'border-black bg-gray-50 text-black font-medium'
                            : 'border-gray-200 text-gray-500 hover:bg-gray-50'
                        }
          `}>
                        <input
                            type="radio"
                            name="viz"
                            value="none"
                            checked={visualization === 'none'}
                            onChange={() => setVisualization('none')}
                            className="hidden"
                        />
                        Standard
                    </label>
                    <label className={`
            flex-1 p-3 rounded-lg border cursor-pointer transition-all flex items-center justify-center gap-2
            ${visualization === 'flow'
                            ? 'border-black bg-gray-50 text-black font-medium ring-1 ring-black'
                            : 'border-gray-200 text-gray-500 hover:bg-gray-50'
                        }
          `}>
                        <input
                            type="radio"
                            name="viz"
                            value="flow"
                            checked={visualization === 'flow'}
                            onChange={() => setVisualization('flow')}
                            className="hidden"
                        />
                        Optical Flow
                    </label>
                </div>
            </div>

            <button
                onClick={handleStart}
                className="w-full py-4 bg-black text-white font-medium rounded-lg shadow-xl hover:bg-gray-800 transition-transform active:scale-[0.99] flex items-center justify-center gap-2"
            >
                <Play className="w-5 h-5 fill-current" />
                Start Interpolation
            </button>
        </div>
    )
}

export default ConfigPanel
