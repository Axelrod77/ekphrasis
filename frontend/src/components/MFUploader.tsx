import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useUploadCAS } from '../hooks/useMutualFunds'

export default function MFUploader() {
  const upload = useUploadCAS()

  const onDrop = useCallback((files: File[]) => {
    if (files[0]) upload.mutate(files[0])
  }, [upload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
  })

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        isDragActive ? 'border-primary-400 bg-primary-50' : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      <input {...getInputProps()} />
      {upload.isPending ? (
        <p className="text-gray-500">Processing PDF...</p>
      ) : (
        <div>
          <p className="text-gray-600 font-medium">Drop your CAS PDF here or click to upload</p>
          <p className="text-xs text-gray-400 mt-1">Supports CAMS & KFintech CAS statements</p>
        </div>
      )}
    </div>
  )
}
