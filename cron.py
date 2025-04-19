import axios from "axios";

// Environment variables
const TAVILY_URL = process.env.TAVILY_URL || "https://api.tavily.com/search";
const TAVILY_API_KEY = process.env.TAVILY_API_KEY;
const RESEND_URL = process.env.RESEND_URL || "https://api.resend.com/emails";
const RESEND_API_KEY = process.env.RESEND_API_KEY;
const SEARCH_QUERY = process.env.SEARCH_QUERY;
const SEARCH_TOPIC = process.env.SEARCH_TOPIC || "news";
const SEARCH_DEPTH = process.env.SEARCH_DEPTH || "advanced";
const SEARCH_DAYS = Number(process.env.SEARCH_DAYS) || 7;
const INCLUDE_ANSWER = process.env.INCLUDE_ANSWER || "false";
const MAX_RESULTS = Number(process.env.MAX_RESULTS) || 10;
const EMAIL_FROM = process.env.EMAIL_FROM;
const EMAIL_TO = process.env.EMAIL_TO;
const EMAIL_SUBJECT = process.env.EMAIL_SUBJECT;

// Main function
async function main() {
  try {
    // Search and extract URLs
    const urls = await searchAndExtractUrls();
    console.log(`Found ${urls.length} results`);

    // Send email with results
    await sendEmail(urls);
    console.log("Email sent successfully");
  } catch (error) {
    console.error("Error in cron job:", error);
    process.exit(1);
  }
}

// Function to search and extract URLs
async function searchAndExtractUrls(): Promise<string[]> {
  try {
    const response = await axios.post(TAVILY_URL, {
      api_key: TAVILY_API_KEY,
      query: SEARCH_QUERY,
      search_depth: SEARCH_DEPTH,
      topic: SEARCH_TOPIC,
      days: SEARCH_DAYS,
      max_results: MAX_RESULTS,
      include_answer: INCLUDE_ANSWER,
    });

    // Extract URLs from results
    return (response.data.results || []).map((result: any) => result.url);
  } catch (error) {
    console.error("Tavily API error:", error);
    throw new Error("Failed to search for results");
  }
}

// Function to send email with URLs
async function sendEmail(urls: string[]): Promise<void> {
  // Create HTML content with URLs
  const htmlContent = `
    <h2>News results for: "${SEARCH_QUERY}"</h2>
    <p>Found ${urls.length} results:</p>
    <ul>
      ${urls.map((url) => `<li><a href="${url}">${url}</a></li>`).join("")}
    </ul>
  `;

  try {
    // Use Resend API directly
    await axios.post(
      RESEND_URL,
      {
        from: EMAIL_FROM,
        to: EMAIL_TO,
        subject: EMAIL_SUBJECT,
        html: htmlContent,
      },
      {
        headers: {
          Authorization: `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
      }
    );
  } catch (error) {
    console.error("Resend API error:", error);
    throw new Error("Failed to send email");
  }
}

// Run the job
main().catch(console.error);
export default main;
