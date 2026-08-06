import type { Metadata } from "next";
import { notFound } from "next/navigation";
import MarketLanding from "../../components/MarketLanding";
import { CATEGORIES, CATEGORY_SLUGS, isCategorySlug } from "../../../config/categories";
import { resolveLpVariant } from "../../../lib/resolve-lp-variant";
import "../au.css";

type Props = {
  params: Promise<{ category: string }>;
  searchParams: Promise<{ variant?: string }>;
};

export function generateStaticParams() {
  return CATEGORY_SLUGS.map((category) => ({ category }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { category } = await params;
  if (!isCategorySlug(category)) return { title: "Not found" };
  const cat = CATEGORIES[category];
  return {
    title: cat.title.au,
    description: cat.description.au,
    robots: { index: false, follow: false },
  };
}

export default async function AUCategoryPage({ params, searchParams }: Props) {
  const { category } = await params;
  if (!isCategorySlug(category)) notFound();
  const sp = await searchParams;
  const variant = await resolveLpVariant(sp);
  return <MarketLanding market="au" category={category} variant={variant} />;
}
