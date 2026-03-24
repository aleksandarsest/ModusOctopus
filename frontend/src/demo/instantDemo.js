const launchBrief = `Aurora Circle is a fictional consumer AI companion and life-assistant app aimed at students and young adults.

Today Aurora Circle launches "Pathfinder Copilot", a new premium AI mode positioned as a high-trust guide for life planning, deadlines, housing choices, mental load, and difficult personal decisions.

Within hours of launch, screenshots spread showing Pathfinder Copilot confidently fabricating serious personal, medical, and legal claims. In several examples it presents false information as if it were verified fact and encourages users to act on it.

The company has not paused the launch. Product marketing still describes Pathfinder Copilot as a calm, reliable everyday planning companion.

Aurora Circle now needs to predict how the backlash spreads on launch day, who amplifies it first, how the narrative shifts from one product failure into a wider AI safety and regulation panic, and which groups turn the story into a symbol of platform-level risk.`

const viralUserPosts = `Launch-day reactions and screenshots:

1. A college student posts that Pathfinder Copilot confidently claimed their university had opened an emergency legal process for lease disputes and told them to start filing documents that do not exist.

2. Another user shares a screenshot where the assistant states that a specific prescription adjustment is commonly recommended, even though the information is false and phrased with high confidence.

3. A creator on short-form video calls the app "a fake certainty machine for stressed young people" and says the problem is not that it makes mistakes, but that it sounds trusted and emotionally calm while being wrong.

4. Safety-minded users begin comparing Aurora Circle to other AI products and asking why companion apps with high-trust framing are allowed to present fabricated medical and legal guidance without stronger restrictions.

5. Tech commentary accounts post side-by-side screenshots and frame the incident as the moment consumer AI crossed from "annoying hallucinations" into "dangerous authority theater".`

const policyAndResponseNotes = `Internal notes and early response context:

- Pathfinder Copilot was marketed around confidence, daily planning, and dependable support for young adults.
- The launch team expected a strong creator-led adoption curve and planned a large trust-centered campaign.
- Communications prepared a soft statement focused on "edge cases" and "rapid model iteration", but no full rollback language has been approved.
- Internal safety reviewers previously warned that high-trust phrasing could magnify harm when the system is wrong, especially in health, legal, and relationship-advice contexts.
- Policy observers are already asking whether companion-style AI products should face stricter labeling, age protections, or launch approval standards.
- Product leadership wants to keep momentum if possible. Safety and comms teams think the story could become a broader AI regulation flashpoint before the end of the day.`

export function getInstantDemoConfig() {
  return {
    title: 'AI companion launch-day backlash',
    graphBackend: 'local',
    llmConfig: {
      provider_type: 'codex_cli',
      executable: 'codex'
    },
    simulationRequirement: `Scenario:
Aurora Circle launches Pathfinder Copilot, a consumer AI companion and life-assistant feature for students and young adults.

Timing:
This is a launch-day backlash. Harmful screenshots begin spreading within hours of release.

Key stakeholders:
Young users, parents, creators, safety advocates, journalists, AI critics, policy voices, and Aurora Circle leadership.

Main question:
Predict how the backlash spreads once users discover that Pathfinder Copilot fabricates serious personal, medical, and legal claims with confidence.

Success or risk to evaluate:
Model how the narrative escalates from a product launch issue into platform-wide panic about AI safety and regulation, and identify which voices amplify that shift first.`,
    documents: [
      {
        name: 'launch-brief.txt',
        type: 'text/plain',
        content: launchBrief
      },
      {
        name: 'viral-user-posts.txt',
        type: 'text/plain',
        content: viralUserPosts
      },
      {
        name: 'policy-and-response-notes.txt',
        type: 'text/plain',
        content: policyAndResponseNotes
      }
    ]
  }
}

const quickLaunchBrief = `Helio Pixel, a niche hardware startup, launches "Aurora Clips", adaptive smart glasses that surface contextual productivity tips.

Public preview attendees are already sharing short clips saying the framing looks like a full launch, and a few comments point out the messaging feels like a mixed permissioned release.

The team wants a safe, fast simulation that treats this as a completed launch day so they can review the early reaction arc in under two minutes.`

const quickLaunchSignals = `Quick reaction notes:

1. A creator hypes Aurora Clips as the "next wearable hero" and posts a demo asking followers which productivity problem the glasses should solve next.
2. An industry analyst notes the release timing aligns with a funding announcement and questions whether the glasses team scoped up too fast for the initial rollout.
3. Two engineers mention the hardware needs fine-tuning for low-light and want to signal that in future updates without dampening current momentum.
4. A safety advocate simply asks if adaptive glassware needs new privacy disclosures before it reaches more users.`

export function getQuickProductLaunchDemoConfig() {
  return {
    title: 'Quick Aurora Clips product launch',
    graphBackend: 'local',
    llmConfig: {
      provider_type: 'codex_cli',
      executable: 'codex'
    },
    simulationRequirement: `Scenario:
Product launch for Helio Pixel's Aurora Clips adaptive productivity glasses.

Timing:
Live launch-day chatter from a small creator wave and analyst coverage.

Key stakeholders:
Creators, industry analysts, hardware engineers, safety experts, Helio Pixel leadership.

Main question:
Predict the initial narrative the launch sparks and how those early signals could expand into broader trust or privacy concerns.

Success or risk to evaluate:
Track whether the launch survives the first few hours and what support, clarification, or privacy assurance pulls the story toward acceptance.`,
    documents: [
      {
        name: 'quick-launch-brief.txt',
        type: 'text/plain',
        content: quickLaunchBrief
      },
      {
        name: 'quick-launch-signals.txt',
        type: 'text/plain',
        content: quickLaunchSignals
      }
    ]
  }
}
