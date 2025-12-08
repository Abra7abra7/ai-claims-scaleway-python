"use client"

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { FileBarChart, Download, Loader2, Calendar } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'

export default function ReportsPage() {
  const t = useTranslations('reports')
  const tCommon = useTranslations('common')

  const [reportType, setReportType] = useState<string>('summary')
  const [format, setFormat] = useState<string>('pdf')
  const [dateFrom, setDateFrom] = useState<string>('')
  const [dateTo, setDateTo] = useState<string>('')
  const [isGenerating, setIsGenerating] = useState(false)

  const handleGenerate = async () => {
    setIsGenerating(true)
    
    // Simulate report generation
    await new Promise((resolve) => setTimeout(resolve, 2000))
    
    toast.success('Report generated successfully')
    setIsGenerating(false)
  }

  return (
    <div className="container py-6 max-w-2xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
        <p className="text-muted-foreground">{t('subtitle')}</p>
      </div>

      {/* Report Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileBarChart className="h-5 w-5" />
            {t('generateReport')}
          </CardTitle>
          <CardDescription>
            Configure and generate reports
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Report Type */}
          <div className="space-y-2">
            <Label>Report Type</Label>
            <Select value={reportType} onValueChange={setReportType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="summary">{t('summaryReport')}</SelectItem>
                <SelectItem value="claim">{t('claimReport')}</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Date Range */}
          <div className="space-y-2">
            <Label>{t('dateRange')}</Label>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">{t('from')}</Label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="date"
                    className="pl-9"
                    value={dateFrom}
                    onChange={(e) => setDateFrom(e.target.value)}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">{t('to')}</Label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="date"
                    className="pl-9"
                    value={dateTo}
                    onChange={(e) => setDateTo(e.target.value)}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Format */}
          <div className="space-y-2">
            <Label>{t('format')}</Label>
            <Select value={format} onValueChange={setFormat}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pdf">PDF</SelectItem>
                <SelectItem value="json">JSON</SelectItem>
                <SelectItem value="csv">CSV</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Generate Button */}
          <Button
            className="w-full"
            onClick={handleGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {t('generating')}
              </>
            ) : (
              <>
                <Download className="mr-2 h-4 w-4" />
                {t('generateReport')}
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Quick Reports */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Reports</CardTitle>
          <CardDescription>
            Generate common reports with one click
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <Button variant="outline" className="h-auto py-4 flex-col">
              <FileBarChart className="h-8 w-8 mb-2" />
              <span>Last 7 Days Summary</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col">
              <FileBarChart className="h-8 w-8 mb-2" />
              <span>Monthly Summary</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col">
              <FileBarChart className="h-8 w-8 mb-2" />
              <span>Processing Times</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col">
              <FileBarChart className="h-8 w-8 mb-2" />
              <span>Error Report</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

