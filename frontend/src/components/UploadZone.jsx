import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud } from 'lucide-react'

const UploadZone = ({ onUpload }) => {
    const onDrop = useCallback(acceptedFiles => {
        if (acceptedFiles.length > 0) {
            onUpload(acceptedFiles[0])
        }
    }, [onUpload])

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'video/*': ['.mp4', '.mov', '.avi']
        },
        maxFiles: 1
    })

    return (
        <div
            {...getRootProps()}
            className={`
        w-full py-20 px-8 border border-dashed rounded-lg cursor-pointer transition-all duration-200
        flex flex-col items-center justify-center gap-4 group
        ${isDragActive
                    ? 'border-black bg-gray-50'
                    : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                }
      `}
        >
            <input {...getInputProps()} />
            <div className={`p-4 rounded-full bg-gray-100 group-hover:bg-white transition-colors`}>
                <UploadCloud className="w-8 h-8 text-gray-600" />
            </div>
            <div className="text-center">
                <p className="text-lg font-medium text-gray-900">
                    Upload Video
                </p>
                <p className="text-sm text-gray-500 mt-1">
                    Drag & drop or click to select
                </p>
            </div>
        </div>
    )
}

export default UploadZone
