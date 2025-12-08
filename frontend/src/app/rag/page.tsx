"use client"

import { useState, useCallback } from 'react'
import { useTranslations } from 'next-intl'
import { useDropzone } from 'react-dropzone'
import {
  Upload,
  Search,
  Trash2,
  FileText,
  Database,
  Loader2,
  CheckCircle,
  Clock,
  MoreHorizontal,
  FolderOpen,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'
import { useRAGDocuments, useUploadRAGDocument, useDeleteRAGDocument } from '@/hooks/use-rag'
import { format } from 'date-fns'

const categories = ['policy', 'procedure', 'guideline', 'template'] as const
const countries = ['SK', 'IT', 'DE'] as const

export default function RAGPage() {
  const t = useTranslations('rag')
  const tCommon = useTranslations('common')
  const tCountries = useTranslations('countries')

  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [countryFilter, setCountryFilter] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')
  const [uploadOpen, setUploadOpen] = useState(false)
  const [deleteId, setDeleteId] = useState<number | null>(null)
  
  // Upload form state
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploadCountry, setUploadCountry] = useState<string>('SK')
  const [uploadCategory, setUploadCategory] = useState<string>('policy')

  const { data: documents, isLoading } = useRAGDocuments({
    country: countryFilter || undefined,
    category: categoryFilter || undefined,
  })
  const uploadMutation = useUploadRAGDocument()
  const deleteMutation = useDeleteRAGDocument()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setUploadFile(acceptedFiles[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    multiple: false,
  })

  const handleUpload = async () => {
    if (!uploadFile) return
    
    await uploadMutation.mutateAsync({
      file: uploadFile,
      country: uploadCountry,
      category: uploadCategory,
    })
    
    setUploadOpen(false)
    setUploadFile(null)
  }

  const handleDelete = async () => {
    if (deleteId) {
      await deleteMutation.mutateAsync(deleteId)
      setDeleteId(null)
    }
  }

  const filteredDocuments = documents?.filter((doc) =>
    searchQuery ? doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) : true
  )

  return (
    <div className="container py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
          <p className="text-muted-foreground">{t('subtitle')}</p>
        </div>
        <Dialog open={uploadOpen} onOpenChange={setUploadOpen}>
          <DialogTrigger asChild>
            <Button>
              <Upload className="mr-2 h-4 w-4" />
              {t('uploadDocument')}
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t('uploadDocument')}</DialogTitle>
              <DialogDescription>
                Upload a document to the knowledge base
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
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
                {uploadFile ? (
                  <div className="flex items-center justify-center gap-2">
                    <FileText className="h-5 w-5" />
                    <span className="font-medium">{uploadFile.name}</span>
                  </div>
                ) : (
                  <>
                    <Upload className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">
                      Drop a file here or click to select
                    </p>
                  </>
                )}
              </div>

              {/* Country */}
              <div className="space-y-2">
                <Label>Country</Label>
                <Select value={uploadCountry} onValueChange={setUploadCountry}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {countries.map((c) => (
                      <SelectItem key={c} value={c}>
                        {tCountries(c)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Category */}
              <div className="space-y-2">
                <Label>{t('category')}</Label>
                <Select value={uploadCategory} onValueChange={setUploadCategory}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((c) => (
                      <SelectItem key={c} value={c}>
                        {t(`categories.${c}`)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setUploadOpen(false)}>
                {tCommon('cancel')}
              </Button>
              <Button
                onClick={handleUpload}
                disabled={!uploadFile || uploadMutation.isPending}
              >
                {uploadMutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Upload className="mr-2 h-4 w-4" />
                )}
                {tCommon('upload')}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder={t('searchDocuments')}
                  className="pl-9"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Select value={countryFilter} onValueChange={setCountryFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Country" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All countries</SelectItem>
                  {countries.map((c) => (
                    <SelectItem key={c} value={c}>
                      {tCountries(c)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder={t('category')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All categories</SelectItem>
                  {categories.map((c) => (
                    <SelectItem key={c} value={c}>
                      {t(`categories.${c}`)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Filename</TableHead>
                <TableHead>Country</TableHead>
                <TableHead>{t('category')}</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>{t('chunks')}</TableHead>
                <TableHead>Created</TableHead>
                <TableHead className="w-20">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-6 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                    <TableCell><Skeleton className="h-8 w-8" /></TableCell>
                  </TableRow>
                ))
              ) : filteredDocuments?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                    <Database className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    {tCommon('noResults')}
                  </TableCell>
                </TableRow>
              ) : (
                filteredDocuments?.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        {doc.filename}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{tCountries(doc.country as 'SK' | 'IT' | 'DE')}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        <FolderOpen className="mr-1 h-3 w-3" />
                        {t(`categories.${doc.category as 'policy' | 'procedure' | 'guideline' | 'template'}`)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {doc.is_processed ? (
                        <Badge variant="default" className="bg-success">
                          <CheckCircle className="mr-1 h-3 w-3" />
                          {t('processed')}
                        </Badge>
                      ) : (
                        <Badge variant="secondary">
                          <Clock className="mr-1 h-3 w-3" />
                          {t('pending')}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>{doc.chunk_count}</TableCell>
                    <TableCell>
                      {doc.created_at ? format(new Date(doc.created_at), 'PP') : '-'}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => setDeleteId(doc.id)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            {tCommon('delete')}
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Stats */}
      {filteredDocuments && filteredDocuments.length > 0 && (
        <div className="text-sm text-muted-foreground">
          {filteredDocuments.length} documents •{' '}
          {filteredDocuments.filter((d) => d.is_processed).length} processed •{' '}
          {filteredDocuments.reduce((sum, d) => sum + d.chunk_count, 0)} total chunks
        </div>
      )}

      {/* Delete confirmation */}
      <AlertDialog open={deleteId !== null} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{tCommon('confirm')}</AlertDialogTitle>
            <AlertDialogDescription>
              {t('deleteConfirm')}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{tCommon('cancel')}</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {tCommon('delete')}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

