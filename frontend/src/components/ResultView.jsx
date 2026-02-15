import React, { useRef, useEffect, useState } from 'react'
import { Download, RefreshCw, CheckCircle, Smartphone, Monitor, Play, Pause, Volume2, VolumeX } from 'lucide-react'
import { ReactCompareSlider, ReactCompareSliderImage } from 'react-compare-slider';

const ResultView = ({ url, originalUrl, onReset }) => {
    const video1Ref = useRef(null);
    const video2Ref = useRef(null);
    const [isPlaying, setIsPlaying] = useState(true);
    const [isMuted, setIsMuted] = useState(true);

    // Sync videos attempt
    useEffect(() => {
        const v1 = video1Ref.current;
        const v2 = video2Ref.current;

        if (!v1 || !v2) return;

        const sync = () => {
            if (Math.abs(v1.currentTime - v2.currentTime) > 0.1) {
                v2.currentTime = v1.currentTime;
            }
        };

        // Check sync every frame
        let animationFrameId;
        const loop = () => {
            sync();
            animationFrameId = requestAnimationFrame(loop);
        };
        loop();

        return () => cancelAnimationFrame(animationFrameId);
    }, []);

    const togglePlay = () => {
        const v1 = video1Ref.current;
        const v2 = video2Ref.current;

        if (isPlaying) {
            v1.pause();
            v2.pause();
        } else {
            v1.play();
            v2.play();
        }
        setIsPlaying(!isPlaying);
    };

    const toggleMute = () => {
        setIsMuted(!isMuted);
    };

    return (
        <div className="w-full animate-fade-in">
            <div className="text-center mb-6">
                <div className="inline-flex items-center gap-2 px-4 py-1 bg-green-50 text-green-700 rounded-full border border-green-100 mb-4">
                    <CheckCircle className="w-3 h-3" />
                    <span className="text-xs font-medium">Interpolation Complete</span>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Before & After</h2>
            </div>

            <div className="relative group">
                <div className="aspect-video bg-gray-100 rounded-xl overflow-hidden shadow-xl mb-6 border border-gray-200">
                    <ReactCompareSlider
                        itemOne={
                            <div className="w-full h-full relative">
                                <div className="absolute top-4 left-4 bg-black/50 text-white px-2 py-0.5 rounded text-[10px] font-medium z-10 backdrop-blur-sm">Original</div>
                                <video
                                    ref={video2Ref}
                                    src={originalUrl}
                                    className="w-full h-full object-contain"
                                    muted={isMuted}
                                    loop
                                    playsInline
                                />
                            </div>
                        }
                        itemTwo={
                            <div className="w-full h-full relative">
                                <div className="absolute top-4 right-4 bg-black/50 text-white px-2 py-0.5 rounded text-[10px] font-medium z-10 backdrop-blur-sm">Processed</div>
                                <video
                                    ref={video1Ref}
                                    src={url}
                                    className="w-full h-full object-contain"
                                    muted={isMuted}
                                    loop
                                    playsInline
                                />
                            </div>
                        }
                        style={{ width: '100%', height: '100%' }}
                    />
                </div>

                {/* Floating Controls */}
                <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex items-center gap-2 px-4 py-2 bg-black/80 backdrop-blur-md rounded-full text-white shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <button onClick={togglePlay} className="hover:text-blue-400 p-1">
                        {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current" />}
                    </button>
                    <div className="w-px h-4 bg-white/20"></div>
                    <button onClick={toggleMute} className="hover:text-blue-400 p-1">
                        {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <a
                    href={url}
                    download
                    className="py-3 px-6 bg-black text-white font-medium rounded-lg shadow-lg hover:bg-gray-800 transition-all flex items-center justify-center gap-2 text-sm"
                >
                    <Download className="w-4 h-4" />
                    Download
                </a>

                <button
                    onClick={onReset}
                    className="py-3 px-6 bg-white border border-gray-200 text-gray-900 font-medium rounded-lg hover:bg-gray-50 transition-all flex items-center justify-center gap-2 text-sm"
                >
                    <RefreshCw className="w-4 h-4" />
                    Process New
                </button>
            </div>
        </div>
    )
}

export default ResultView
