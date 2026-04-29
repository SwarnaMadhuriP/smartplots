export type Plot = {
  id: number;
  title: string;
  description?: string;
  image: string;
  location: string;
  price: string;
  acres: string;
  zone: string;
  matchScore: number;
  appreciation: string;
  rentalDemand: string;
  liquidity: string;
  riskLevel: string;
  reasons: string[];
  aiReasons?: string[];
  highlights: string[];
};
