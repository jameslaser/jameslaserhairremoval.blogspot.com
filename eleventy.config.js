import { HtmlBasePlugin } from "@11ty/eleventy";
import site from "./src/_data/site.js";

export default function (eleventyConfig) {
  // Adds the GitHub Pages sub-folder (/repo-name/) to every root link at build time.
  eleventyConfig.addPlugin(HtmlBasePlugin);
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });

  // Blogger-imported HTML can contain {{ }} or {% %}; never treat post bodies as templates.
  eleventyConfig.setTemplateFormats(["njk", "md", "html", "11ty.js"]);

  // ---------- Collections ----------
  eleventyConfig.addCollection("posts", (api) =>
    api.getFilteredByGlob("src/posts/**/*.{md,html}").filter((p) => !p.data.draft).reverse()
  );

  eleventyConfig.addCollection("labels", (api) => {
    const counts = new Map();
    for (const p of api.getFilteredByGlob("src/posts/**/*.{md,html}")) {
      if (p.data.draft) continue;
      for (const l of p.data.labels || []) counts.set(l, (counts.get(l) || 0) + 1);
    }
    return [...counts.entries()]
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
  });

  // ---------- Filters ----------
  const fmt = (d, opts) => new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Riyadh", ...opts }).format(new Date(d));
  eleventyConfig.addFilter("readableDate", (d) => fmt(d, { day: "numeric", month: "long", year: "numeric" }));
  eleventyConfig.addFilter("isoDate", (d) => new Date(d).toISOString());

  // Labels can be Arabic, so keep Unicode letters instead of transliterating.
  const labelSlug = (s) =>
    String(s).trim().toLowerCase().normalize("NFC")
      .replace(/['’]/g, "")
      .replace(/[^\p{L}\p{N}]+/gu, "-")
      .replace(/^-+|-+$/g, "");
  eleventyConfig.addFilter("labelSlug", labelSlug);
  eleventyConfig.addGlobalData("labelSlug", () => labelSlug);

  eleventyConfig.addFilter("excerpt", (post, words = 32) => {
    if (post.data.description) return post.data.description;
    const html = String(post.content || "").replace(/<(script|style|table|h[1-6])[\s\S]*?<\/\1>/gi, " ");
    const paras = html.match(/<p[\s>][\s\S]*?<\/p>/gi);
    const text = (paras ? paras.join(" ") : html)
      .replace(/<[^>]+>/g, " ")
      .replace(/&nbsp;/g, " ")
      .replace(/&amp;/g, "&")
      .replace(/\s+/g, " ")
      .trim();
    const parts = text.split(" ");
    return parts.length > words ? parts.slice(0, words).join(" ") + "…" : text;
  });

  eleventyConfig.addFilter("firstImage", (post) => {
    if (post.data.image) return post.data.image;
    const m = String(post.content || "").match(/<img[^>]+src=["']([^"']+)["']/i);
    return m ? m[1] : null;
  });

  eleventyConfig.addFilter("readingTime", (html) => {
    const words = String(html || "").replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length;
    return Math.max(1, Math.round(words / 200)) + " min read";
  });

  eleventyConfig.addFilter("postsWithLabel", (posts, label) =>
    posts.filter((p) => (p.data.labels || []).includes(label))
  );

  eleventyConfig.addFilter("limit", (arr, n) => (arr || []).slice(0, n));
  eleventyConfig.addFilter("fullUrl", (path) => new URL(String(path).replace(/^\//, ""), site.url).href);


  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "_site" },
    pathPrefix: process.env.PATH_PREFIX || "/",
    htmlTemplateEngine: false,
    markdownTemplateEngine: false,
  };
}
