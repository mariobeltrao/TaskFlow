import {Github,Instagram,Mail} from 'lucide-react';
import {Brand} from './Brand';

export function Footer({compact=false,className=''}:{compact?:boolean;className?:string}){
  return <footer className={`site-footer ${compact?'footer-compact':''} ${className}`.trim()}>
    <Brand compact/>
    <p>TaskFlow · Fundado por Mário Beltrão</p>
    <div className="footer-links">
      <a href="https://www.instagram.com/mariobeltraoo_/" target="_blank" rel="noopener noreferrer" aria-label="Instagram de Mário Beltrão"><Instagram/></a>
      <a href="mailto:mario16bleal@gmail.com" aria-label="Enviar e-mail para Mário Beltrão"><Mail/></a>
      <a href="https://github.com/mariobeltrao" target="_blank" rel="noopener noreferrer" aria-label="GitHub de Mário Beltrão"><Github/></a>
    </div>
  </footer>;
}
