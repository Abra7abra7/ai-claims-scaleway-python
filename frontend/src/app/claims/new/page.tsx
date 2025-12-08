"use client"

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useDropzone } from 'react-dropzone'
import { Upload, X, FileText, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import { useCreateClaim } from '@/hooks/use-claims'

export default function NewClaimPage() {
  const t = useTranslations('claims')
  const tCommon = useTranslations('common')
  const tCountries = useTranslations('countries')
  const router = useRouter()
  
  const [country, setCountry] = useState<string>('SK')
  const [files, setFiles] = useState<File[]>([])
  
  const createMutation = useCreateClaim()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
    },
    multiple: true,
  })

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = async () => {
    if (files.length === 0) return
    
    try {
      const result = await createMutation.mutateAsync({ country, files })
      router.push(`/claims/${result.id}`)
    } catch (error) {
      // Error handled by mutation
    }
  }

  return (
    <div className="container py-6 max-w-2xl">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('newClaim')}</h1>
          <p className="text-muted-foreground">{t('uploadDocuments')}</p>
        </div>

        {/* Country Selection */}
        <Card>
          <CardHeader>
            <CardTitle>{t('country')}</CardTitle>
            <CardDescription>Select the country for this claim</CardDescription>
          </CardHeader>
          <CardContent>
            <Select value={country} onValueChange={setCountry}>
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="SK">{tCountries('SK')}</SelectItem>
                <SelectItem value="IT">{tCountries('IT')}</SelectItem>
                <SelectItem value="DE">{tCountries('DE')}</SelectItem>
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {/* File Upload */}
        <Card>
          <CardHeader>
            <CardTitle>{t('uploadDocuments')}</CardTitle>
            <CardDescription>{t('supportedFormats')}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={cn(
                'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
                isDragActive
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/25 hover:border-primary/50'
              )}
            >
              <input {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-sm text-muted-foreground">
                {t('dropFiles')}
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                {t('supportedFormats')}
              </p>
            </div>

            {/* File List */}
            {files.length > 0 && (
              <div className="space-y-2">
                <Label>Selected files ({files.length})</Label>
                <div className="space-y-2">
                  {files.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 rounded-lg border bg-muted/50"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <p className="text-sm font-medium">{file.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {(file.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeFile(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Submit */}
        <div className="flex justify-end gap-4">
          <Button variant="outline" onClick={() => router.back()}>
            {tCommon('cancel')}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={files.length === 0 || createMutation.isPending}
          >
            {createMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {tCommon('loading')}
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                {tCommon('upload')}
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}

