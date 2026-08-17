import type { Metadata } from "next";
import { notFound } from "next/navigation";
import GuidedMatchLanding from "../../components/GuidedMatchLanding";
import { CATEGORIES, CATEGORY_SLUGS, isCategorySlug } from "../../../config/categories";
import { resolveLpVariant } from "../../../lib/resolve-lp-variant";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";

type Props = {
  params: Promise<{ category: string }>;
  searchParams: Promise<{ variant?: string }>;
};

export function generateStaticParams() {
  return CATEGORY_SLUGS.map((category) => ({ category }));
}

/** Static siblings (/us/capacity, /quiz, /consult) win. Unknown slugs 404. */
export const dynamicParams = false;

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { category } = await params;
  if (!isCategorySlug(category)) return { title: "Not found" };
  const cat = CATEGORIES[category];
  return buildPageMetadata({
    title: cat.title.us,
    description: cat.description.us,
    path: `/us/${category}`,
    indexable: true,
    ogImage: "/brand/hero-us-2026.jpg",
  });
}

export default async function USCategoryPage({ params, searchParams }: Props) {
  const { category } = await params;
  if (!isCategorySlug(category)) notFound();
  const variant = await resolveLpVariant(await searchParams);
  return (
    <GuidedMatchLanding
      market="us"
      category={category}
      variant={variant}
      careersHref={resolveCareersUrl()}
    />
  );
}
