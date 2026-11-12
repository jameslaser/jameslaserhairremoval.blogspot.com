// Defaults for every article in this folder.
// Article addresses match Blogger's pattern (/2026/11/my-post.html),
// so links shared from the old blog can point to the same paths here.
export default {
  layout: "layouts/post.njk",
  labels: [],
  eleventyComputed: {
    permalink: (data) => {
      if (data.draft) return false;
      // Imported posts keep their exact Blogger address.
      if (data.bloggerPath) return data.bloggerPath;
      const d = new Date(data.page.date);
      const parts = new Intl.DateTimeFormat("en-CA", {
        timeZone: "Asia/Riyadh", year: "numeric", month: "2-digit",
      }).formatToParts(d);
      const y = parts.find((p) => p.type === "year").value;
      const m = parts.find((p) => p.type === "month").value;
      return `/${y}/${m}/${data.slug || data.page.fileSlug}.html`;
    },
    ogImage: (data) => data.image || null,
    jsonld: (data) =>
      JSON.stringify({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        headline: data.title,
        datePublished: new Date(data.page.date).toISOString(),
        author: { "@type": "Person", name: data.site.author.name, jobTitle: data.site.author.title },
        publisher: { "@type": "MedicalClinic", name: data.site.clinic.name, address: data.site.clinic.address },
        inLanguage: ["en", "ar"],
      }),
  },
};
