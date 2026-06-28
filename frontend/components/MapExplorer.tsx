'use client';

import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet';
import { Plot } from '@/data/mockPlots';

type Props = {
  plots: Plot[];
  selectedPlotId: number | null;
  onSelectPlot: (id: number) => void;
};

export default function MapExplorer({
  plots,
  selectedPlotId,
  onSelectPlot,
}: Props) {
  const plotsWithCoordinates = plots.filter(
    (plot) =>
      typeof plot.latitude === 'number' && typeof plot.longitude === 'number',
  );

  return (
    <section className="rounded-[2rem] border border-[#E7D3CC] bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-bold text-slate-900">Map Explorer</h1>

      <p className="mt-1 text-sm text-slate-500">
        Explore available plots by location.
      </p>

      <div className="mt-6 h-[620px] overflow-hidden rounded-[2rem] border border-[#E7D3CC]">
        <MapContainer
          center={[30.2672, -97.7431]}
          zoom={6}
          scrollWheelZoom
          className="h-full w-full"
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {plotsWithCoordinates.map((plot) => (
            <Marker
              key={plot.id}
              position={[plot.latitude, plot.longitude]}
              icon={L.divIcon({
                className: '',
                html: `
                  <div style="
                    width: 18px;
                    height: 18px;
                    background: ${
                      selectedPlotId === plot.id ? '#C7745A' : '#D8B4A6'
                    };
                    border: 3px solid white;
                    border-radius: 9999px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                  "></div>
                `,
                iconSize: [18, 18],
                iconAnchor: [9, 9],
              })}
              eventHandlers={{
                click: () => {
                  onSelectPlot(Number(plot.id));
                },
              }}
            >
              <Popup>
                <button
                  onClick={() => onSelectPlot(Number(plot.id))}
                  className="min-w-[180px] text-left"
                >
                  <p className="font-semibold text-slate-900">{plot.title}</p>

                  <p className="mt-1 text-sm text-slate-500">{plot.location}</p>

                  <p className="mt-2 text-sm font-bold text-[#B8644C]">
                    {plot.price}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">{plot.acres}</p>
                </button>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {plotsWithCoordinates.length === 0 && (
        <p className="mt-4 text-sm text-red-500">
          No plots with coordinates found.
        </p>
      )}
    </section>
  );
}
