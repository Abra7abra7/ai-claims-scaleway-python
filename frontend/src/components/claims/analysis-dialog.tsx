"use client"

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { Zap, Loader2, Sparkles, ChevronDown, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
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
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { usePrompts, useStartAnalysis } from '@/hooks/use-claims'

interface AnalysisDialogProps {
  claimId: number
  disabled?: boolean
  onSuccess?: () => void
}

export function AnalysisDialog({ claimId, disabled, onSuccess }: AnalysisDialogProps) {
  const t = useTranslations('analysis')
  const tCommon = useTranslations('common')
  
  const [open, setOpen] = useState(false)
  const [selectedPrompt, setSelectedPrompt] = useState<string>('')
  
  const { data: promptsData, isLoading: isLoadingPrompts } = usePrompts()
  const startAnalysisMutation = useStartAnalysis()

  // Set default prompt when data loads
  if (promptsData && !selectedPrompt) {
    setSelectedPrompt(promptsData.default || promptsData.prompts[0]?.id || '')
  }

  const handleStartAnalysis = async () => {
    if (!selectedPrompt) return
    
    await startAnalysisMutation.mutateAsync({ 
      claimId, 
      promptId: selectedPrompt 
    })
    
    setOpen(false)
    onSuccess?.()
  }

  const selectedPromptDetails = promptsData?.prompts.find(p => p.id === selectedPrompt)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button disabled={disabled}>
          <Zap className="mr-2 h-4 w-4" />
          {t('runAnalysis')}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            {t('selectPrompt')}
          </DialogTitle>
          <DialogDescription>
            {t('selectPromptDescription')}
          </DialogDescription>
        </DialogHeader>
        
        <div className="py-4 space-y-4">
          {isLoadingPrompts ? (
            <div className="space-y-3">
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
            </div>
          ) : promptsData?.prompts.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No prompts configured
            </div>
          ) : (
            <ScrollArea className="h-[300px] pr-4">
              <RadioGroup
                value={selectedPrompt}
                onValueChange={setSelectedPrompt}
                className="space-y-3"
              >
                {promptsData?.prompts.map((prompt) => (
                  <Label
                    key={prompt.id}
                    htmlFor={`prompt-${prompt.id}`}
                    className={`flex cursor-pointer rounded-lg border p-4 transition-colors hover:bg-muted/50 ${
                      selectedPrompt === prompt.id 
                        ? 'border-primary bg-primary/5' 
                        : 'border-muted'
                    }`}
                  >
                    <RadioGroupItem
                      value={prompt.id}
                      id={`prompt-${prompt.id}`}
                      className="sr-only"
                    />
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{prompt.name}</span>
                        <Badge variant="outline" className="ml-2">
                          {prompt.llm_model}
                        </Badge>
                      </div>
                      {prompt.description && (
                        <p className="text-sm text-muted-foreground">
                          {prompt.description}
                        </p>
                      )}
                      {promptsData.default === prompt.id && (
                        <Badge variant="secondary" className="mt-1">
                          Default
                        </Badge>
                      )}
                    </div>
                  </Label>
                ))}
              </RadioGroup>
            </ScrollArea>
          )}
          
          {selectedPromptDetails && (
            <Card className="bg-muted/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Selected Prompt</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{selectedPromptDetails.name}</span>
                  <Badge>{selectedPromptDetails.llm_model}</Badge>
                </div>
                {selectedPromptDetails.description && (
                  <p className="text-xs text-muted-foreground">
                    {selectedPromptDetails.description}
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            {tCommon('cancel')}
          </Button>
          <Button 
            onClick={handleStartAnalysis}
            disabled={!selectedPrompt || startAnalysisMutation.isPending}
          >
            {startAnalysisMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Zap className="mr-2 h-4 w-4" />
            )}
            {t('startAnalysis')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

