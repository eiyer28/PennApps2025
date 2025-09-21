import Head from "next/head";
import Image from "next/image";
import { Geist, Geist_Mono } from "next/font/google";
import styles from "@/styles/Home.module.css";
import { useEffect, useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/dist/ScrollTrigger";
import Card from "./card.jsx";
import Cloud from "./cloud.jsx";
import MenuButton from "./menu-button.jsx";
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
  const cloud1 = useRef(null);
  const cloud2 = useRef(null);
  const cloud3 = useRef(null);
  const cloud4 = useRef(null);
  const cloud5 = useRef(null);
  const cloud6 = useRef(null);
  const cloud7 = useRef(null);
  const cloud8 = useRef(null);

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
        { ref: cloud8, name: 'cloud8', y: 60, rotation: -4 }
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
            <Image src="/assets/logo-with-white.svg" width={100} height={100} style={{marginBottom: '20px'}}/>
            <h1 className={styles.title}>
              Offset your carbon footprint, <br />
              know you're having an impact
            </h1>
            <div style={{paddingTop: "px"}}>
              <p className={styles.landingbody}>
              Let's get started
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
            <div ref={cloud2} style={{position: 'absolute', top: '30%', right: '40%'}}>
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
                width={400} 
                height={400}
                type="outline"
              />
            </div>
            <div ref={cloud6} style={{position: 'absolute', top: '100%', left: '20%'}}>
              <Cloud 
                width={200} 
                height={200}
                type="outline"
              />
            </div>
            <div ref={cloud7} style={{position: 'absolute', top: '140%', right: '200px'}}>
              <Cloud 
                width={100} 
                height={100}
                type="solid"
              />
            </div>
            <div ref={cloud8} style={{position: 'absolute', top: '170%', right: '30%'}}>
              <Cloud 
                width={400} 
                height={400}
                type="solid"
              />
            </div>
            <div style={{position: 'absolute', top: '155%', left: '1%'}}>
              <Cloud 
                width={300} 
                height={300}
                type="solid"
              />
            </div>
          </div>
        </div>

        <div className={styles.fullsection}>
          <h2 className={styles.subtitle} style={{marginBottom: '20px'}}>
            About us
          </h2>
          <p className={styles.landingbody} style={{textAlign: 'center'}}>
            Those with the money that can fund sustainable development 
            are not being connected with the people and places that are 
            engineering the solutions that can meaningfully affect our 
            own carbon output and our own development of our cities and 
            societies. <br></br> <br></br>

            We aim to solve this problem by creating a platform that utilizes
            blockchain as a regulatory structure to ensure traceability 
            and completion of these projects. 
          </p>

        </div>

        <div className={styles.fullsection} style={{backgroundColor: 'var(--maincolor)'}}>
          <h2 className={styles.subtitle}>
            Start here, start now
          </h2>
          <div className={styles.cardgrids}>
            <Card 
            height="350px"
            width="400px"
            title="Buy Carbon Offsets"
            content="Browse possible projects to support and offset your carbon footprint, starting as small as a few cents."
            link="/projects"
            />
            <Card 
              height="350px"
              width="400px"
              title="Supply Projects"
              content="Support verified sustainable development projects around the world."
              link="/supply-projects"
            />
          </div>
        </div>
      </div>
    </>
  );
}