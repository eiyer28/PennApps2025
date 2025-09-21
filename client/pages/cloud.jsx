import Image from "next/image";

export default function Cloud({ 
  height = 100, 
  width = 100, 
  left, 
  right, 
  top, 
  bottom, 
  type = "solid", // "solid" or "outline"
  z = -1
}) {
  const cloudStyle = {
    position: 'absolute',
    ...(width && { width }),
    ...(height && { height }),
    ...(left && { left }),
    ...(right && { right }),
    ...(top && { top }),
    ...(bottom && { bottom }),
    zIndex: z,
    pointerEvents: 'none'
  };

  const cloudSrc = type === "outline" ? "/assets/cloud-outline.svg" : "/assets/cloud.svg";

  return (
    <div style={cloudStyle}>
      <Image 
        src={cloudSrc}
        alt="Cloud" 
        width={width}
        height={height}
      />
    </div>
  );
}