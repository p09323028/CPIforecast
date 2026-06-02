export const CATEGORY_ORDER = [
  "Food",
  "FAFH",
  "meats",
  "pork",
  "beef",
  "poultry",
  "seafood",
  "eggs",
  "egg",
  "dairy",
  "milk",
  "vegetable",
  "fruit",
  "oils",
] as const;

export type CategoryEn = (typeof CATEGORY_ORDER)[number];

export const CATEGORY_ZH: Record<string, string> = {
  Food: "食物類",
  FAFH: "外食費",
  meats: "肉類",
  pork: "豬肉",
  beef: "牛肉",
  poultry: "雞肉",
  seafood: "水產品",
  eggs: "蛋類",
  egg: "雞蛋",
  dairy: "乳類",
  milk: "鮮乳",
  vegetable: "蔬菜",
  fruit: "水果",
  oils: "食用油",
};

export const CATEGORY_ICON: Record<string, string> = {
  Food: "🍱",
  FAFH: "🥢",
  meats: "🥩",
  pork: "🐷",
  beef: "🐄",
  poultry: "🐔",
  seafood: "🐟",
  eggs: "🥚",
  egg: "🍳",
  dairy: "🧀",
  milk: "🥛",
  vegetable: "🥬",
  fruit: "🍎",
  oils: "🫒",
};

export const zh = (en: string) => CATEGORY_ZH[en] ?? en;
export const icon = (en: string) => CATEGORY_ICON[en] ?? "·";
