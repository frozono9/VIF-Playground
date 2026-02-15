import { useState, useEffect } from 'react'
import axios from 'axios'
import UploadZone from './components/UploadZone'
import ConfigPanel from './components/ConfigPanel'
import ProcessingStatus from './components/ProcessingStatus'
import ResultView from './components/ResultView'
import { Film } from 'lucide-react'

// Backend URL
const API_URL = 'http://localhost:8000';

function App() {
  const [step, setStep] = useState('upload'); // upload, config, processing, result
  const [file, setFile] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [resultUrl, setResultUrl] = useState(null);
  const [error, setError] = useState(null);

  const handleUpload = async (uploadedFile) => {
    setFile(uploadedFile);
    setError(null);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const response = await axios.post(`${API_URL}/upload`, formData);
      setMetadata(response.data);
      setStep('config');
    } catch (err) {
      console.error(err);
      setError('Upload failed. Please try again.');
    }
  };

  const startProcessing = async (multiplier, visualization) => {
    setError(null);
    try {
      const response = await axios.post(`${API_URL}/process`, {
        filename: metadata.filename,
        multiplier: multiplier,
        visualization: visualization
      });
      setTaskId(response.data.task_id);
      setStep('processing');
    } catch (err) {
      console.error(err);
      setError('Failed to start processing.');
    }
  };

  useEffect(() => {
    let interval;
    if (step === 'processing' && taskId) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`${API_URL}/status/${taskId}`);
          const { status, progress, result_url, error } = response.data;

          setProgress(progress);

          if (status === 'completed') {
            setResultUrl(`${API_URL}${result_url}`);
            setStep('result');
            clearInterval(interval);
          } else if (status === 'failed') {
            setError(error || 'Processing failed.');
            setStep('config'); // Go back to config on failure
            clearInterval(interval);
          }
        } catch (err) {
          console.error(err);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [step, taskId]);

  const reset = () => {
    setStep('upload');
    setFile(null);
    setMetadata(null);
    setTaskId(null);
    setProgress(0);
    setResultUrl(null);
    setError(null);
  };

  return (
    <div className="min-h-screen flex flex-col items-center py-12 px-4 bg-white">
      <div className="w-full max-w-2xl">
        <header className="mb-12 text-center border-b border-gray-100 pb-8">
          <h1 className="text-4xl font-bold text-gray-900 tracking-tight mb-2">
            VFI Playground
          </h1>
          <p className="text-gray-500 text-lg">AI Video Interpolation Engine</p>
        </header>

        <main>
          {error && (
            <div className="mb-6 p-4 bg-red-50 text-red-600 border border-red-100 rounded-md text-sm text-center">
              {error}
            </div>
          )}

          {step === 'upload' && <UploadZone onUpload={handleUpload} />}

          {step === 'config' && metadata && (
            <ConfigPanel
              metadata={metadata}
              onStart={startProcessing}
              onBack={() => setStep('upload')}
            />
          )}

          {step === 'processing' && (
            <ProcessingStatus progress={progress} />
          )}

          {step === 'result' && resultUrl && (
            <ResultView
              url={resultUrl}
              originalUrl={file ? URL.createObjectURL(file) : null}
              onReset={reset}
            />
          )}
        </main>

        <footer className="mt-16 text-center text-sm text-gray-400">
          Powered by RIFE & PyTorch
        </footer>
      </div>
    </div>
  )
}

export default App
