import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Historical supply chain disruption data
HISTORICAL_DISRUPTIONS = [
    {
        "title": "Suez Canal Blockage 2021",
        "content": """
        In March 2021, the Ever Given container ship ran aground in the Suez Canal,
        blocking one of the world's most critical shipping routes for 6 days.
        The canal handles approximately 12% of global trade.
        The blockage delayed an estimated $9.6 billion worth of trade per day.
        Industries most affected: Electronics, Automotive, Oil and Gas, Consumer Goods.
        Ships were forced to reroute around the Cape of Good Hope adding 7-14 days to journeys.
        After the blockage was cleared, port congestion took weeks to normalize.
        Total estimated economic impact: $54-60 billion.
        Recovery time: 3-4 weeks for shipping schedules to normalize.
        """,
        "metadata": {"type": "blockage", "location": "Suez Canal", "year": "2021", "severity": "Critical"}
    },
    {
        "title": "COVID-19 Port Shutdowns 2020-2021",
        "content": """
        During COVID-19 pandemic, major ports worldwide faced shutdowns and severe congestion.
        Port of Yantian in China shut down for 2 weeks in May 2021 causing massive backlogs.
        Port of Los Angeles and Long Beach faced record congestion with 100+ ships waiting.
        Global container shortage caused shipping rates to increase by 500-1000%.
        Industries affected: All manufacturing sectors, Retail, Electronics, Automotive.
        Average shipping delays: 4-8 weeks beyond normal transit times.
        Recovery time: 12-18 months for global supply chains to normalize.
        Container shortage lasted through 2022.
        """,
        "metadata": {"type": "pandemic", "location": "Global", "year": "2020-2021", "severity": "Critical"}
    },
    {
        "title": "Red Sea Attacks 2023-2024",
        "content": """
        Starting late 2023, Houthi rebels began attacking commercial vessels in the Red Sea.
        The Red Sea handles approximately 15% of global trade and 30% of container traffic.
        Major shipping companies including Maersk, MSC, CMA CGM rerouted ships around Africa.
        Rerouting added 10-14 days and $1 million extra fuel costs per voyage.
        Industries affected: European imports from Asia, Oil and Gas, Consumer Electronics.
        Shipping rates on Asia-Europe routes increased by 200-300%.
        Insurance costs for vessels in the region increased significantly.
        Recovery dependent on regional security situation.
        """,
        "metadata": {"type": "geopolitical", "location": "Red Sea", "year": "2023-2024", "severity": "High"}
    },
    {
        "title": "Taiwan Strait Tensions 2022",
        "content": """
        Military tensions around Taiwan Strait in August 2022 raised concerns about
        semiconductor supply chain disruptions.
        Taiwan produces 60% of the world's semiconductors and 90% of advanced chips.
        Companies began stockpiling chips in anticipation of potential disruptions.
        Industries affected: Electronics, Automotive, AI/Technology sectors globally.
        Shipping routes through Taiwan Strait carry significant Asia-Pacific trade.
        Insurance premiums for vessels near Taiwan increased.
        Long term impact: Accelerated semiconductor manufacturing diversification globally.
        """,
        "metadata": {"type": "geopolitical", "location": "Taiwan Strait", "year": "2022", "severity": "High"}
    },
    {
        "title": "Port of Rotterdam Strike 2022",
        "content": """
        Workers at the Port of Rotterdam, Europe's largest port, conducted strikes in 2022.
        Rotterdam handles 14.8 million TEUs annually and is Europe's main gateway.
        Strike caused delays of 3-5 days for vessels waiting to dock.
        Industries affected: European manufacturing, Consumer goods, Chemical industry.
        Knock-on effects felt across European supply chains for 2-3 weeks.
        Alternative ports like Antwerp and Hamburg saw increased congestion.
        Recovery time: 2-3 weeks after strike resolution.
        """,
        "metadata": {"type": "strike", "location": "Rotterdam", "year": "2022", "severity": "Medium"}
    },
    {
        "title": "Strait of Malacca Piracy Risks",
        "content": """
        The Strait of Malacca is one of the world's most important shipping lanes.
        Over 80,000 vessels pass through annually carrying 25% of global trade.
        Periodic piracy incidents cause vessels to increase security measures.
        Insurance costs increase during high piracy periods.
        Industries affected: All Asia-Pacific trade routes, Oil tankers especially.
        Average delay during high risk periods: 1-3 days for security checks.
        Alternative route: Lombok Strait adds 2-3 days to journeys.
        """,
        "metadata": {"type": "piracy", "location": "Strait of Malacca", "year": "ongoing", "severity": "Medium"}
    },
    {
        "title": "Panama Canal Drought 2023",
        "content": """
        Severe drought in 2023 reduced water levels in the Panama Canal significantly.
        Canal authority reduced daily transits from 36 to 24 vessels.
        Ships were required to reduce cargo loads to comply with draft restrictions.
        Wait times increased to 3-4 weeks from the normal 1-2 days.
        Industries affected: US East Coast imports, LNG shipments, Container trade.
        Shipping companies rerouted some vessels via Suez Canal.
        Economic impact estimated at $200 million per week in delays.
        Recovery dependent on rainfall and water reservoir levels.
        """,
        "metadata": {"type": "weather", "location": "Panama Canal", "year": "2023", "severity": "High"}
    },
    {
        "title": "China Port Congestion 2021",
        "content": """
        Multiple Chinese ports faced severe congestion throughout 2021.
        Yantian port closure due to COVID cases caused 2 week backlog.
        Ningbo-Zhoushan port partial closure in August 2021 lasted 2 weeks.
        China handles approximately 30% of global container throughput.
        Industries affected: Global electronics, Retail, Manufacturing supply chains.
        Average additional delays: 3-6 weeks during peak congestion.
        Shipping rates from China to US West Coast reached record $20,000 per container.
        Recovery time: 4-6 months for congestion to fully clear.
        """,
        "metadata": {"type": "congestion", "location": "China Ports", "year": "2021", "severity": "Critical"}
    },
    {
        "title": "Russia-Ukraine War Supply Chain Impact 2022",
        "content": """
        Russia's invasion of Ukraine in February 2022 caused massive global supply chain disruptions.
        Ukraine and Russia together supply 30% of the world's wheat and 20% of corn exports.
        Black Sea shipping routes were effectively blocked cutting off critical grain exports.
        Global food prices surged 20-50% affecting developing nations most severely.
        Russia supplies 40% of Europe's natural gas causing energy supply chain crisis.
        Industries affected: Food and Agriculture, Energy, Steel, Fertilizers, Chemicals.
        Ukraine produces 50% of the world's neon gas used in semiconductor manufacturing.
        Fertilizer shortages caused by sanctions on Russia affected global agriculture.
        Shipping insurance for Black Sea routes became unavailable or extremely expensive.
        Average delay impact: Complete route closure for Black Sea shipping.
        Recovery time: Ongoing — partial grain corridor established mid 2022 then collapsed again.
        Economic impact: Contributed to global inflation of 8-10% in 2022-23.
        """,
        "metadata": {"type": "geopolitical", "location": "Black Sea", "year": "2022", "severity": "Critical"}
    },
    {
        "title": "Japan Earthquake and Tsunami Supply Chain Crisis 2011",
        "content": """
        The 9.0 magnitude earthquake and tsunami in March 2011 devastated Japan's northeast coast.
        Japan is a critical supplier of automotive parts, electronics components, and specialty chemicals.
        Toyota, Honda, and Nissan shut down production globally due to parts shortages.
        Global automotive production fell by 30% in the months following the disaster.
        Japan supplies 60% of the world's silicon wafers used in semiconductor manufacturing.
        Renesas Electronics — supplier of 40% of auto microcontrollers — was severely damaged.
        Industries affected: Automotive, Electronics, Semiconductors, Chemicals.
        Companies discovered dangerous over-reliance on single source Japanese suppliers.
        Average production delays: 3-6 months for automotive manufacturers globally.
        Recovery time: 6-12 months for most supply chains, 2+ years for some specialized components.
        This event became the defining case study for supply chain single point of failure risk.
        Insurance losses exceeded $35 billion making it one of the costliest disasters ever.
        """,
        "metadata": {"type": "natural_disaster", "location": "Japan", "year": "2011", "severity": "Critical"}
    },
    {
        "title": "Global Semiconductor Shortage 2020-2023",
        "content": """
        COVID-19 pandemic triggered a global semiconductor chip shortage lasting over 3 years.
        Automotive companies cancelled chip orders in 2020 expecting demand drop.
        Consumer electronics demand surged as people worked from home buying laptops and devices.
        When auto demand recovered, chip foundries had allocated capacity to consumer electronics.
        TSMC and Samsung — producing 80% of the world's advanced chips — could not scale fast enough.
        Ford and GM shut down plants losing billions in revenue due to chip shortages.
        Average vehicle production was down 7.7 million units globally in 2021 alone.
        Industries affected: Automotive, Consumer Electronics, Industrial Equipment, Medical Devices.
        New car prices increased 20-30% due to shortage and inventory constraints.
        Chip lead times extended from 12 weeks to 52+ weeks at peak shortage.
        Companies began holding 3-6 months of chip inventory instead of just-in-time approach.
        Recovery time: Gradual improvement through 2022-23, full recovery by late 2023.
        Long term impact: $500 billion in new chip factory investments announced globally.
        """,
        "metadata": {"type": "shortage", "location": "Global", "year": "2020-2023", "severity": "Critical"}
    },
    {
        "title": "US-China Trade War Impact 2018-2020",
        "content": """
        The US-China trade war beginning in 2018 fundamentally reshaped global supply chains.
        US imposed tariffs of 25% on $250 billion worth of Chinese goods.
        China retaliated with tariffs on $110 billion of US agricultural and industrial goods.
        Companies began relocating manufacturing from China to Vietnam, Mexico, India, Bangladesh.
        Apple shifted some iPhone production to India and Vietnam.
        Electronics, Apparel, Furniture, and Industrial goods supply chains restructured entirely.
        Industries affected: Electronics, Automotive, Agriculture, Steel, Chemicals, Retail.
        US soybean exports to China fell 75% devastating American farmers.
        Shipping volumes between US and China dropped 25% at peak trade war tensions.
        Companies faced increased costs of 15-25% during supply chain restructuring.
        Vietnam's exports to US increased 35% as manufacturing shifted from China.
        Long term impact: Accelerated China Plus One strategy across all major multinationals.
        Recovery: Phase One deal signed January 2020 but structural changes proved permanent.
        """,
        "metadata": {"type": "trade_policy", "location": "US-China", "year": "2018-2020", "severity": "High"}
    },
    {
        "title": "Los Angeles and Long Beach Port Strike 2023",
        "content": """
        ILWU dockworkers at Ports of Los Angeles and Long Beach conducted work slowdowns in 2023.
        These two ports handle 40% of all US container imports making them critical infrastructure.
        Labor disputes caused vessel backlogs and processing delays for months.
        Retailers began diverting shipments to East Coast ports months in advance.
        Industries affected: US Retail, Consumer Electronics, Automotive parts, Agriculture exports.
        Companies importing holiday goods faced severe uncertainty about delivery timelines.
        Port of Houston and Savannah saw 30-40% volume increases as shippers diverted cargo.
        Average delays: 5-10 days during peak disruption periods.
        Contract negotiations lasted over a year before resolution in May 2023.
        Economic impact: Estimated $150 million per day in delayed cargo value.
        Long term impact: Companies accelerated East Coast port diversification strategies.
        Recovery time: 4-6 weeks after contract resolution for backlogs to clear.
        """,
        "metadata": {"type": "strike", "location": "Los Angeles", "year": "2023", "severity": "High"}
    }
]

def initialize_knowledge_base():
    """
    Creates ChromaDB vector store from historical disruption data.
    """
    print("Initializing knowledge base...")

    # Set up Gemini embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GEMINI_API_KEY
    )

    # Convert historical data to LangChain Documents
    documents = []
    for disruption in HISTORICAL_DISRUPTIONS:
        doc = Document(
            page_content=f"{disruption['title']}\n\n{disruption['content']}",
            metadata=disruption['metadata']
        )
        documents.append(doc)

    # Create ChromaDB vector store
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    print(f"Knowledge base initialized with {len(documents)} historical disruptions")
    return vectorstore


def load_knowledge_base():
    """
    Loads existing ChromaDB vector store.
    """
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GEMINI_API_KEY
    )

    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )

    return vectorstore


def search_similar_disruptions(query, k=3):
    """
    Searches knowledge base for disruptions similar to the query.
    Returns top k most relevant historical events.
    """
    vectorstore = load_knowledge_base()
    results = vectorstore.similarity_search(query, k=k)

    print(f"\nFound {len(results)} similar historical disruptions:")
    for i, result in enumerate(results):
        print(f"\n--- Match {i+1} ---")
        print(f"Location: {result.metadata.get('location')}")
        print(f"Type: {result.metadata.get('type')}")
        print(f"Severity: {result.metadata.get('severity')}")
        print(f"Content preview: {result.page_content[:150]}...")

    return results


if __name__ == "__main__":
    # Initialize the knowledge base
    initialize_knowledge_base()

    # Test search
    print("\n--- Testing similarity search ---")
    search_similar_disruptions("port strike causing shipping delays in Europe")