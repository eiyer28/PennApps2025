import Head from "next/head";
import Image from "next/image";
import { Geist, Geist_Mono } from "next/font/google";
import styles from "@/styles/Home.module.css";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/dist/ScrollTrigger";
import Card from "./card.jsx";
import Cloud from "./cloud.jsx";
import MenuBar from "./menu-bar.jsx";
import Button from "./button.jsx";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

export default function Home() {
  const [isSpinning, setIsSpinning] = useState(false);
  const [currentRotation, setCurrentRotation] = useState(0);
  const spinSpeedRef = useRef(0);
  const animationRef = useRef();
  
  const cloud1 = useRef(null);
  const cloud2 = useRef(null);
  const cloud3 = useRef(null);
  const cloud4 = useRef(null);
  const cloud5 = useRef(null);
  const cloud6 = useRef(null);
  const cloud7 = useRef(null);
  const cloud8 = useRef(null);
  const cloud9 = useRef(null);

  const container = useRef(null);

  useLayoutEffect(() => {
    const context = gsap.context(() => {
      const cloudRefs = [
        { ref: cloud1, name: 'cloud1', y: 100, rotation: 5 },
        { ref: cloud2, name: 'cloud2', y: 80, rotation: -10 },
        { ref: cloud3, name: 'cloud3', y: 60, rotation: 5 },
        { ref: cloud4, name: 'cloud4', y: 90, rotation: -5 },
        { ref: cloud5, name: 'cloud5', y: 120, rotation: 8 },
        { ref: cloud6, name: 'cloud6', y: 90, rotation: -8 },
        { ref: cloud7, name: 'cloud7', y: 40, rotation: 4 },
        { ref: cloud8, name: 'cloud8', y: 60, rotation: -4 },
        { ref: cloud9, name: 'cloud9', y: 150, rotation: 6 }
      ];

      cloudRefs.forEach(cloud => {
        if (cloud.ref.current) {
          gsap.to(cloud.ref.current, {
            y: cloud.y,
            rotation: cloud.rotation,
            ease: "none",
            scrollTrigger: {
              trigger: container.current,
              start: "top bottom",
              end: "bottom top",
              scrub: 1
            }
          });
        }
      });
    }, container);
    
    return () => context.revert();
  }, []);

  useEffect(() => {
    if (isSpinning) {
      const animate = () => {
        // Accelerate until max speed
        const maxSpeed = 8; // Maximum degrees per frame
        const acceleration = 0.005; // Reduced from 0.01 to 0.005 for even more gradual acceleration
        spinSpeedRef.current = Math.min(spinSpeedRef.current + acceleration, maxSpeed);
        
        setCurrentRotation(prevRotation => {
          const newRotation = (prevRotation + spinSpeedRef.current) % 360;
          return newRotation;
        });
        
        animationRef.current = requestAnimationFrame(animate);
      };
      animationRef.current = requestAnimationFrame(animate);
    } else {
      // Reset speed when stopping but keep current rotation
      spinSpeedRef.current = 0;
    }
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isSpinning]);

  const handleLogoClick = () => {
    setIsSpinning(!isSpinning);
  };

  return ( 
    <>
      <Head>
        <title>CarbonChain</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <MenuBar />

      <div style={{backgroundColor: 'white', position: 'relative'}}>
        <div className={styles.landingsection} style={{backgroundColor: 'white'}}>
          {/* Text content with higher z-index */}
          <div style={{position: 'relative', zIndex: 3}}>
            <Image 
              src="/assets/logo-with-white.svg" 
              width={100} 
              height={100} 
              style={{
                marginBottom: '20px',
                transform: `rotate(${currentRotation}deg)`,
                cursor: 'pointer'
              }}
              onClick={handleLogoClick}
            />
            <style jsx>{`
              @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
              }
            `}</style>
            <h1 className={styles.title}>
              Offset your carbon footprint, <br />
              know <span className={styles.highlightText}>where your money is going</span>
            </h1>
            <div style={{paddingTop: "10px"}}>
              <p className={styles.landingbody} style={{fontSize: "24px"}}>
              Let's get started!
              </p>
            </div>
          </div>

          {/* Background clouds with lower z-index - separate container for parallax */}
          <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 1}} ref={container}>
            <div ref={cloud1} style={{position: 'absolute', top: '-35%', right: '30%'}}>
              <Cloud 
                width={550} 
                height={550}
                type="solid"
              />
            </div>
            <div ref={cloud2} style={{position: 'absolute', top: '30%', right: '35%'}}>
              <Cloud 
                width={300} 
                height={300}
                type="outline"
              />
            </div>
            <div ref={cloud3} style={{position: 'absolute', top: '65%', left: '25%'}}>
              <Cloud 
                width={150} 
                height={150}
                type="solid"
              />
            </div>
            <div ref={cloud4} style={{position: 'absolute', top: '70%', right: '25%'}}>
              <Cloud 
                width={200} 
                height={200}
                type="solid"
              />
            </div>
            <div ref={cloud5} style={{position: 'absolute', top: '60%', left: '-5%'}}>
              <Cloud 
                width={470} 
                height={470}
                type="outline"
              />
            </div>
            <div ref={cloud6} style={{position: 'absolute', top: '110%', left: '20%'}}>
              <Cloud 
                width={250} 
                height={250}
                type="outline"
              />
            </div>
            <div ref={cloud7} style={{position: 'absolute', top: '135%', right: '200px'}}>
              <Cloud 
                width={100} 
                height={100}
                type="solid"
              />
            </div>
            <div ref={cloud8} style={{position: 'absolute', top: '170%', right: '30%'}}>
              <Cloud 
                width={500} 
                height={500}
                type="solid"
              />
            </div>
            <div ref={cloud9} style={{position: 'absolute', top: '150%', left: '3%'}}>
              <Cloud 
                width={300} 
                height={300}
                type="solid"
              />
            </div>
          </div>
        </div>

        <div className={styles.fullsection} style={{position: 'relative', zIndex: 2}}>
          <Card 
            height="auto"
            width="700px"
            title={<span className={styles.highlightText}>Our Purpose</span>}
            content={
              <>
                Those with the money that can fund sustainable development 
                are not being connected with the people and places that are 
                engineering the solutions that can <u>meaningfully affect</u> our 
                own carbon output and our own development of our cities and 
                societies. <br></br> <br></br>

                We aim to solve this problem by creating a platform that utilizes
                blockchain as a regulatory structure to ensure <u>traceability</u>  
                and <u>transparency</u> of these projects.
              </>
            }
            showBorder={true}
            titleFontSize="24px"
            contentFontSize="18px"
            padding="30px"
            button={true}
          />
        </div>

        <div className={styles.fullsection} style={{backgroundColor: 'var(--maincolor)'}}>
          <h2 className={styles.subtitle} style={{color: 'white'}}>
            <span className={styles.highlightText}>Start here, start now</span>
          </h2>
          <div className={styles.cardgrids}>
            <Card 
            height="500px"
            width="400px"
            title="Buy Carbon Offsets"
            content="Browse verified projects to support and offset your carbon footprint, starting as small as a few cents."
            image="/assets/yzy.jpg"
            link="/search"
            showBorder={false}
            />
          </div>
        </div>
      </div>
    </>
  );
}