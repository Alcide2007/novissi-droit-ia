import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/** Rendu Markdown sûr : le HTML brut n'est PAS interprété (react-markdown l'ignore par défaut) et les liens sont isolés. */
export default function Markdown({ text }: { text: string }) {
  return (
    <div className="md">
      <ReactMarkdown remarkPlugins={[remarkGfm]}
        components={{ a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer nofollow">{children}</a> }}>
        {text}
      </ReactMarkdown>
    </div>
  );
}
