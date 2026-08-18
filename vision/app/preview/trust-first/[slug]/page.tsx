import type { Metadata } from "next";
import { notFound } from "next/navigation";
import TrustFirstLanding from "../../../components/trust-first/TrustFirstLanding";
import {
  isTrustFirstPageKey,
  TRUST_FIRST_PAGE_KEYS,
  trustFirstPage,
} from "../../../../config/trust-first";
import {
  assignTrustFirstVariant,
  previewPageMetadata,
} from "../../../../lib/trust-first";

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ v?: string }>;
};

export function generateStaticParams() {
  return TRUST_FIRST_PAGE_KEYS.map((slug) => ({ slug }));
}

export const dynamicParams = false;

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  if (!isTrustFirstPageKey(slug)) return { title: "Not found", robots: { index: false } };
  return previewPageMetadata(trustFirstPage(slug));
}

export default async function TrustFirstPreviewPage({ params, searchParams }: Props) {
  const { slug } = await params;
  const query = await searchParams;
  if (!isTrustFirstPageKey(slug)) notFound();
  const page = trustFirstPage(slug);
  const { variant } = assignTrustFirstVariant({ query: query.v });
  return <TrustFirstLanding page={page} variant={variant} />;
}
