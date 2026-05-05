import { getAssetFrameSpec } from "../lib/assetFrameSpecs";

function parseSize(value, fallback) {
  const match = /^(\d+)/.exec(value ?? "");
  return match ? Number(match[1]) : fallback;
}

function buildSliceEntries(frame) {
  const topHeight = parseSize(frame.slices.top.dimensions, 12);
  const rightWidth = parseSize(frame.slices.right.dimensions, 12);
  const bottomHeight = parseSize(frame.slices.bottom.dimensions, 12);
  const leftWidth = parseSize(frame.slices.left.dimensions, 12);
  const cornerWidth = parseSize(frame.slices.topLeft.dimensions, 20);
  const cornerHeight = parseSize(frame.slices.topLeft.dimensions.split(" x ")[1], cornerWidth);

  return [
    {
      id: "top-left",
      slot: "is-corner",
      meta: frame.slices.topLeft,
      style: { top: 0, left: 0, width: `${cornerWidth}px`, height: `${cornerHeight}px` },
    },
    {
      id: "top",
      slot: "is-edge",
      meta: frame.slices.top,
      style: { top: 0, left: `${cornerWidth}px`, right: `${cornerWidth}px`, height: `${topHeight}px` },
    },
    {
      id: "top-right",
      slot: "is-corner",
      meta: frame.slices.topRight,
      style: { top: 0, right: 0, width: `${cornerWidth}px`, height: `${cornerHeight}px` },
    },
    {
      id: "left",
      slot: "is-edge",
      meta: frame.slices.left,
      style: {
        top: `${cornerHeight}px`,
        left: 0,
        bottom: `${cornerHeight}px`,
        width: `${leftWidth}px`,
      },
    },
    {
      id: "center",
      slot: "is-center",
      meta: frame.slices.center,
      style: {
        top: `${topHeight}px`,
        left: `${leftWidth}px`,
        right: `${rightWidth}px`,
        bottom: `${bottomHeight}px`,
      },
    },
    {
      id: "right",
      slot: "is-edge",
      meta: frame.slices.right,
      style: {
        top: `${cornerHeight}px`,
        right: 0,
        bottom: `${cornerHeight}px`,
        width: `${rightWidth}px`,
      },
    },
    {
      id: "bottom-left",
      slot: "is-corner",
      meta: frame.slices.bottomLeft,
      style: { left: 0, bottom: 0, width: `${cornerWidth}px`, height: `${cornerHeight}px` },
    },
    {
      id: "bottom",
      slot: "is-edge",
      meta: frame.slices.bottom,
      style: { left: `${cornerWidth}px`, right: `${cornerWidth}px`, bottom: 0, height: `${bottomHeight}px` },
    },
    {
      id: "bottom-right",
      slot: "is-corner",
      meta: frame.slices.bottomRight,
      style: { right: 0, bottom: 0, width: `${cornerWidth}px`, height: `${cornerHeight}px` },
    },
  ];
}

export function AssetOverlay({ frameId }) {
  const frame = getAssetFrameSpec(frameId);

  if (!frame) {
    return null;
  }

  const slices = buildSliceEntries(frame);

  return (
    <div className="asset-overlay" aria-hidden="true">
      <div className="asset-overlay-frame-label">{frame.label}</div>
      {slices.map((slice) => (
        <div
          className={`asset-overlay-slice ${slice.slot}`}
          key={`${frame.id}-${slice.id}`}
          style={slice.style}
        >
          <div className="asset-overlay-tooltip">
            <strong>{slice.meta.name}</strong>
            <span>{slice.meta.dimensions}</span>
            <span>{slice.meta.resize}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
