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

/** Static siblings (/au/capacity, /quiz, /consult) win. Unknown slugs 404. */
export const dynamicParams = false;

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { category } = await params;
  if (!isCategorySlug(category)) return { title: "Not found" };
  const cat = CATEGORIES[category];
  return buildPageMetadata({
    title: cat.title.au,
    description: cat.description.au,
    path: `/au/${category}`,
    indexable: true,
    ogImage: "/brand/hero-au-2026.jpg",
  });
}

export default async function AUCategoryPage({ params }: Props) {
  const { category } = await params;
  if (!isCategorySlug(category)) notFound();
  return (
    <StaffingBaselineLanding
      market="au"
      category={category}
      careersHref={resolveCareersUrl()}
    />
  );
}
