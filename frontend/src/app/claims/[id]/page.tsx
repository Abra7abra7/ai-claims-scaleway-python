import { AppLayout } from "@/components/layout/app-layout";
import { ClaimDetail } from "@/components/claims/claim-detail";

interface ClaimDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function ClaimDetailPage({ params }: ClaimDetailPageProps) {
  const { id } = await params;
  
  return (
    <AppLayout>
      <ClaimDetail claimId={parseInt(id)} />
    </AppLayout>
  );
}

