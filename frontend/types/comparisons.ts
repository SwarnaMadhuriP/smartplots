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
