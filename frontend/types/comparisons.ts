export type ComparisonPlot = {
  id: number;
  title: string;
  price: number;
  area_acres: number;
  city: string;
  state: string;
  zoning_type: string;
  road_access: boolean;
  water_access: boolean;
  electricity: boolean;
  sewer: boolean;
  risk_notes?: string;
};

export type ComparePlotProfile = {
  plot_id: number;
  award_label: string;
  suitability_score: number;
  key_tradeoff: string;
};

export type ComparisonAnalysis = {
  overall_recommendation: string;
  profiles: ComparePlotProfile[];
  summary_points: string[];
};
