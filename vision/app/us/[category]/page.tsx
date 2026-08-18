import type { Metadata } from "next";
import { notFound } from "next/navigation";
import StaffingBaselineLanding from "../../components/StaffingBaselineLanding";
import { CATEGORIES, CATEGORY_SLUGS, isCategorySlug } from "../../../config/categories";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";

type Props = {
  params: Promise<{ category: string }>;
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

export default async function USCategoryPage({ params }: Props) {
  const { category } = await params;
  if (!isCategorySlug(category)) notFound();
  return (
    <StaffingBaselineLanding
      market="us"
      category={category}
      careersHref={resolveCareersUrl()}
    />
  );
}
