import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import List, Dict, Optional, Tuple
import re
from langchain_openai import ChatOpenAI
from data_processing.pdf_processor import PDFProcessor
from data_processing.csv_processor import CSVProcessor  
from data_processing.embeddings import EmbeddingManager
from config import settings

class EnhancedRAGAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        self.pdf_processor = PDFProcessor()
        self.csv_processor = CSVProcessor()
        self.embedding_manager = EmbeddingManager()
        
        # Load CSV data
        self.csv_processor.process_csv()
        
        # Initialize military terminology and advanced features
        self.military_terms = self._initialize_military_terms()
        self.intent_patterns = self._initialize_intent_patterns()
        self.strategy_matrix = self._initialize_strategy_matrix()

    def _initialize_military_terms(self) -> Dict[str, str]:
        """Initialize comprehensive military terminology mappings."""
        return {
            # Army units and structures
            'squad': 'small military unit typically consisting of 9-13 soldiers',
            'platoon': 'military unit typically consisting of 16-44 soldiers, usually 2-4 squads',
            'company': 'military unit typically consisting of 80-250 soldiers, usually 3-5 platoons',
            'battalion': 'military unit typically consisting of 300-1000 soldiers, usually 3-5 companies',
            'brigade': 'military unit typically consisting of 1500-3200 soldiers, usually 3-5 battalions',
            'division': 'military unit typically consisting of 10000-20000 soldiers, usually 3-4 brigades',
            
            # Military processes and procedures
            'mdmp': 'Military Decision Making Process - systematic approach to problem solving and planning',
            'troop leading procedures': 'TLP - eight-step process used by small unit leaders to plan and prepare for operations',
            'mett-tc': 'Mission, Enemy, Terrain and weather, Troops and support available, Time available, Civil considerations',
            'sop': 'Standard Operating Procedure - set of step-by-step instructions',
            'conop': 'Concept of Operations - verbal or graphic statement that clearly and concisely expresses what the commander intends to accomplish',
            'frago': 'Fragmentary Order - abbreviated form of an operation order issued as needed to change or modify a previous order',
            'fragord': 'Fragmentary Order - abbreviated form of an operation order issued as needed to change or modify a previous order',
            'opord': 'Operation Order - directive issued by a commander to coordinate the execution of an operation',
            'warnord': 'Warning Order - preliminary notice of an order or action which is to follow',
            
            # Staff positions and roles
            's1': 'Personnel Staff Officer - responsible for personnel management, administration, and sustainment',
            's2': 'Intelligence Staff Officer - responsible for intelligence collection, analysis, and dissemination',
            's3': 'Operations Staff Officer - responsible for operations, training, and security',
            's4': 'Logistics Staff Officer - responsible for supply, maintenance, transportation, and services',
            's5': 'Plans Staff Officer - responsible for planning and civil affairs operations',
            's6': 'Signal Staff Officer - responsible for communications and information systems',
            's7': 'Information Operations Staff Officer - responsible for information operations and cyber',
            's8': 'Finance Staff Officer - responsible for financial management and resource management',
            's9': 'Civil Affairs Staff Officer - responsible for civil affairs operations and coordination',
            
            # Training and evaluation
            'acft': 'Army Combat Fitness Test - physical fitness assessment consisting of six events',
            'apft': 'Army Physical Fitness Test - legacy physical fitness test with push-ups, sit-ups, and 2-mile run',
            'ntc': 'National Training Center - premier combat training center located at Fort Irwin, California',
            'jrtc': 'Joint Readiness Training Center - combat training center located at Fort Johnson, Louisiana',
            'ctc': 'Combat Training Center - facility that provides realistic training environments',
            'jmrc': 'Joint Multinational Readiness Center - combat training center located in Germany',
            
            # Awards and decorations
            'aam': 'Army Achievement Medal - decoration for meritorious service or achievement',
            'arcom': 'Army Commendation Medal - decoration for sustained acts of heroism or meritorious service',
            'msm': 'Meritorious Service Medal - decoration for outstanding meritorious achievement or service',
            'bsm': 'Bronze Star Medal - decoration for heroic or meritorious achievement or service',
            'purple heart': 'decoration awarded to members wounded or killed in action',
            
            # Forms and documents
            'da638': 'DA Form 638 - Recommendation for Award form',
            'da31': 'DA Form 31 - Request and Authority for Leave and Earnings Statement',
            'da4856': 'DA Form 4856 - Developmental Counseling Form',
            'da2062': 'DA Form 2062 - Hand Receipt/Annex Number',
            'ncoer': 'Non-Commissioned Officer Evaluation Report - performance evaluation for NCOs',
            'oer': 'Officer Evaluation Report - performance evaluation for officers',
            
            # Combat and tactical terms
            'coa': 'Course of Action - sequence of actions that a commander may follow',
            'ccir': 'Commander\'s Critical Information Requirements - information requirements identified by the commander',
            'pir': 'Priority Intelligence Requirements - intelligence requirements associated with a decision',
            'oir': 'Other Intelligence Requirements - intelligence requirements not associated with a specific decision',
            'isr': 'Intelligence, Surveillance, and Reconnaissance - activities that synchronize sensors, assets, and processing',
            'bda': 'Battle Damage Assessment - evaluation of damage resulting from the application of military force',
            'sitrep': 'Situation Report - report providing information on the current tactical situation',
            'spot report': 'SPOTREP - concise narrative report of essential information covering events or conditions',
            
            # Leadership and development
            'nco': 'Non-Commissioned Officer - enlisted soldier in a position of authority',
            'snco': 'Senior Non-Commissioned Officer - NCO in grades E-7 through E-9',
            'ncopd': 'Non-Commissioned Officer Professional Development - structured development program',
            'ocs': 'Officer Candidate School - program to train enlisted soldiers to become officers',
            'wocs': 'Warrant Officer Candidate School - program to train soldiers to become warrant officers',
            
            # Logistics and supply
            'supply': 'provision of personnel, material, and other items required to sustain military operations',
            'maintenance': 'actions taken to keep equipment in serviceable condition',
            'transportation': 'movement of personnel, equipment, and supplies',
            'sustainment': 'provision of logistics and personnel services necessary to maintain operations',
            'class i': 'subsistence supplies including food and water',
            'class ii': 'general supplies including clothing, individual equipment, and administrative supplies',
            'class iii': 'petroleum, oils, and lubricants',
            'class iv': 'construction and barrier materials',
            'class v': 'ammunition and explosives',
            'class vi': 'personal demand items including food, beverages, and sundries',
            'class vii': 'major end items including vehicles, weapons systems, and equipment',
            'class viii': 'medical supplies and equipment',
            'class ix': 'repair parts and components',
            'class x': 'material to support nonmilitary programs',
            
            # Military document components and formatting terms
            'mission statement': 'concise statement of the task and purpose that defines what the unit must accomplish',
            'execution': 'section of an OPORD that describes how the commander intends to accomplish the mission',
            'scheme of maneuver': 'description of how the commander envisions the operation unfolding',
            'concept of support': 'description of how supporting elements will enable the mission',
            'tasks to subordinate units': 'specific missions assigned to subordinate elements',
            'command and signal': 'information about command relationships and communications',
            'coordinating instructions': 'instructions that apply to two or more units',
            'scheme of fires': 'description of how fires support the maneuver plan',
            'annex': 'appendix to an operation order providing detailed information on specific topics',
            'commanders intent': 'clear, concise statement of what the force must do and the conditions the force must establish',
            'end state': 'desired political and military conditions that define achievement of the commanders objectives'
        }

    def _initialize_intent_patterns(self) -> Dict[str, Dict]:
        """Initialize enhanced intent analysis patterns for better hybrid detection."""
        return {
            'document_generation': {
                'primary_indicators': [
                    'write', 'create', 'generate', 'draft', 'compose', 'prepare', 'develop',
                    'build', 'construct', 'formulate', 'make', 'produce', 'design', 'develop'
                ],
                'secondary_indicators': [
                    'bullet', 'award', 'citation', 'evaluation', 'report', 'memo', 'letter',
                    'recommendation', 'assessment', 'paragraph', 'statement', 'summary',
                    'section', 'annex', 'order', 'brief', 'briefing'
                ],
                'form_indicators': [
                    'da638', 'da31', 'da4856', 'ncoer', 'oer', 'form', 'template',
                    'opord', 'frago', 'fragord', 'conop', 'sitrep', 'spot report'
                ],
                'formatting_indicators': [
                    'phrase', 'format', 'structure', 'section', 'organize', 'layout',
                    'arrange', 'word', 'language', 'tone', 'style', 'presentation',
                    'phrasing', 'wording', 'formatting', 'organization'
                ],
                'weight': 0.8
            },
            'information_retrieval': {
                'primary_indicators': [
                    'what', 'how', 'when', 'where', 'why', 'who', 'explain', 'describe',
                    'tell', 'show', 'list', 'identify', 'define', 'clarify', 'include'
                ],
                'secondary_indicators': [
                    'role', 'responsibility', 'duty', 'process', 'procedure', 'step',
                    'requirement', 'regulation', 'standard', 'guideline', 'policy',
                    'components', 'elements', 'parts', 'contains', 'consists'
                ],
                'knowledge_indicators': [
                    'during', 'in', 'for', 'about', 'regarding', 'concerning', 'involving',
                    'within', 'inside', 'part of', 'component of'
                ],
                'weight': 0.7
            },
            'hybrid_request': {
                'primary_indicators': [
                    'using', 'based on', 'according to', 'following', 'incorporating',
                    'with', 'including', 'considering', 'leveraging', 'per', 'via'
                ],
                'context_indicators': [
                    'situation', 'mission', 'operation', 'training', 'deployment',
                    'exercise', 'scenario', 'environment', 'context', 'for a', 'for an'
                ],
                'complexity_indicators': [
                    'comprehensive', 'detailed', 'thorough', 'complete', 'full',
                    'extensive', 'in-depth', 'elaborate', 'proper', 'correct'
                ],
                'format_knowledge_indicators': [
                    'phrase', 'format', 'structure', 'section', 'how to write',
                    'how to phrase', 'what to include', 'how to organize',
                    'should include', 'should contain', 'goes in', 'belongs in'
                ],
                'document_type_indicators': [
                    'coa statement', 'opord', 'frago', 'fragord', 'conop', 'sitrep', 'spot report',
                    'evaluation', 'assessment', 'briefing', 'estimate', 'annex', 'appendix',
                    'mission statement', 'execution section', 'scheme of maneuver',
                    'concept of support', 'command and signal', 'coordinating instructions'
                ],
                'hybrid_keywords': [
                    'write the', 'draft the', 'create a', 'build a', 'generate the',
                    'list what', 'what goes in', 'what should be in', 'how do i',
                    'what to put in', 'what belongs in', 'components of', 'elements of'
                ],
                'weight': 0.9
            },
            'clarification_needed': {
                'ambiguous_indicators': [
                    'help', 'assist', 'support', 'need', 'want', 'looking for',
                    'guidance', 'advice', 'direction', 'suggestions'
                ],
                'vague_indicators': [
                    'something', 'anything', 'stuff', 'things', 'this', 'that',
                    'it', 'general', 'basic', 'simple'
                ],
                'weight': 0.3
            }
        }

    def _initialize_strategy_matrix(self) -> Dict[str, Dict]:
        """Initialize enhanced strategy determination matrix for better hybrid detection."""
        return {
            'csv_only': {
                'conditions': {
                    'document_generation_high': lambda scores: scores.get('document_generation', 0) >= 0.7 and scores.get('information_retrieval', 0) < 0.3,
                    'form_specific': lambda query: any(form in query.lower() for form in ['da638', 'da31', 'da4856', 'ncoer', 'oer']) and not any(word in query.lower() for word in ['what', 'how', 'explain', 'describe']),
                    'template_only': lambda query: any(word in query.lower() for word in ['template', 'format only', 'structure only']) and not any(word in query.lower() for word in ['doctrine', 'definition', 'explain']),
                    'formatting_focus': lambda query: any(word in query.lower() for word in ['format', 'structure', 'layout']) and not any(doc in query.lower() for doc in ['opord', 'coa', 'frago', 'annex'])
                },
                'confidence_boost': 0.1,
                'prompt_strategy': 'template_focused'
            },
            'pdf_only': {
                'conditions': {
                    'information_retrieval_high': lambda scores: scores.get('information_retrieval', 0) >= 0.6 and scores.get('document_generation', 0) < 0.3,
                    'knowledge_query': lambda query: any(term in query.lower() for term in ['what is', 'explain', 'describe', 'definition of', 'role of']) and not any(word in query.lower() for word in ['write', 'create', 'draft', 'format']),
                    'doctrinal_only': lambda query: any(term in query.lower() for term in ['doctrine', 'regulation', 'manual', 'publication']) and not any(word in query.lower() for word in ['write', 'create', 'draft']),
                    'pure_knowledge': lambda query: query.lower().startswith(('what is', 'explain', 'describe', 'define')) and not any(word in query.lower() for word in ['section', 'paragraph', 'write', 'create'])
                },
                'confidence_boost': 0.1,
                'prompt_strategy': 'knowledge_focused'
            },
            'hybrid_approach': {
                'conditions': {
                    'hybrid_request_high': lambda scores: scores.get('hybrid_request', 0) >= 0.4,
                    'balanced_generation_retrieval': lambda scores: (scores.get('document_generation', 0) >= 0.3 and scores.get('information_retrieval', 0) >= 0.3),
                    'document_plus_knowledge': lambda query: any(doc in query.lower() for doc in ['opord', 'coa', 'frago', 'fragord', 'annex', 'sitrep']) and any(action in query.lower() for action in ['write', 'create', 'draft', 'build', 'generate']),
                    'section_writing': lambda query: any(section in query.lower() for section in ['section', 'paragraph', 'part']) and any(action in query.lower() for action in ['write', 'create', 'draft', 'phrase']),
                    'formatting_with_content': lambda query: any(fmt in query.lower() for fmt in ['phrase', 'format', 'structure', 'include', 'goes in']) and any(doc in query.lower() for doc in ['opord', 'coa', 'frago', 'annex', 'statement']),
                    'what_should_include': lambda query: any(phrase in query.lower() for phrase in ['what should', 'what to include', 'what goes in', 'how do i', 'list what']),
                    'write_with_doctrine': lambda query: any(action in query.lower() for action in ['write', 'draft', 'create', 'build']) and any(doc in query.lower() for doc in ['mission statement', 'execution', 'scheme of maneuver', 'concept of support', 'command and signal']),
                    'military_document_creation': lambda query: len([term for term in ['opord', 'coa', 'frago', 'fragord', 'annex', 'sitrep', 'conop'] if term in query.lower()]) >= 1 and len([action for action in ['write', 'create', 'draft', 'build', 'generate', 'phrase', 'format'] if action in query.lower()]) >= 1
                },
                'confidence_boost': 0.4,
                'prompt_strategy': 'hybrid_reasoning'
            },
            'clarification_required': {
                'conditions': {
                    'ambiguous_high': lambda scores: scores.get('clarification_needed', 0) >= 0.6,
                    'insufficient_context': lambda scores: max(scores.values()) < 0.4 if scores else True,
                    'conflicting_signals': lambda scores: len([s for s in scores.values() if s >= 0.4]) >= 3 if scores else False,
                    'very_short_query': lambda query: len(query.split()) <= 3 and not any(doc in query.lower() for doc in ['opord', 'coa', 'frago'])
                },
                'confidence_boost': 0.0,
                'prompt_strategy': 'clarification'
            }
        }

    def expand_military_terms(self, query: str) -> str:
        """Expand military terminology and acronyms for better understanding."""
        expanded_query = query.lower()
        
        # Track expansions for logging
        expansions_made = []
        
        for term, definition in self.military_terms.items():
            # Create regex pattern for whole word matching
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, expanded_query):
                # Add definition context without replacing the original term
                expansion = f"{term} ({definition})"
                expanded_query = re.sub(pattern, expansion, expanded_query)
                expansions_made.append(term)
        
        return expanded_query

    def analyze_query_intent(self, query: str) -> Dict[str, any]:
        """Perform enhanced intent analysis with better hybrid detection."""
        query_lower = query.lower()
        expanded_query = self.expand_military_terms(query)
        
        intent_scores = {}
        
        # Calculate scores for each intent category
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            indicators_found = []
            
            # Check primary indicators
            if 'primary_indicators' in patterns:
                primary_matches = sum(1 for indicator in patterns['primary_indicators'] 
                                    if indicator in query_lower)
                primary_score = min(primary_matches * 0.3, 1.0) * patterns['weight']
                score += primary_score
                
                if primary_matches > 0:
                    indicators_found.extend([ind for ind in patterns['primary_indicators'] if ind in query_lower])
            
            # Check secondary indicators
            if 'secondary_indicators' in patterns:
                secondary_matches = sum(1 for indicator in patterns['secondary_indicators'] 
                                      if indicator in query_lower)
                secondary_score = min(secondary_matches * 0.2, 0.6) * patterns['weight']
                score += secondary_score
                
                if secondary_matches > 0:
                    indicators_found.extend([ind for ind in patterns['secondary_indicators'] if ind in query_lower])
            
            # Check all other indicator types
            for indicator_type in ['form_indicators', 'knowledge_indicators', 'context_indicators', 
                                 'complexity_indicators', 'ambiguous_indicators', 'vague_indicators',
                                 'formatting_indicators', 'format_knowledge_indicators', 
                                 'document_type_indicators', 'hybrid_keywords']:
                if indicator_type in patterns:
                    matches = sum(1 for indicator in patterns[indicator_type] 
                                if indicator in query_lower)
                    if matches > 0:
                        # Different weights for different indicator types
                        if indicator_type in ['formatting_indicators', 'format_knowledge_indicators', 'hybrid_keywords']:
                            indicator_score = min(matches * 0.25, 0.5) * patterns['weight']
                        elif indicator_type in ['document_type_indicators']:
                            indicator_score = min(matches * 0.3, 0.6) * patterns['weight']
                        else:
                            indicator_score = min(matches * 0.15, 0.4) * patterns['weight']
                        
                        score += indicator_score
                        indicators_found.extend([ind for ind in patterns[indicator_type] if ind in query_lower])
            
            # Enhanced military terminology bonus
            military_term_count = len([term for term in self.military_terms.keys() if term in query_lower])
            military_bonus = min(military_term_count * 0.1, 0.3)
            score += military_bonus
            
            # Special hybrid detection bonuses
            if intent_type == 'hybrid_request':
                # Bonus for document creation with specific military docs
                doc_creation_bonus = 0
                if any(action in query_lower for action in ['write', 'draft', 'create', 'build', 'generate']):
                    if any(doc in query_lower for doc in ['opord', 'coa', 'frago', 'fragord', 'annex']):
                        doc_creation_bonus = 0.3
                
                # Bonus for section/component questions
                section_bonus = 0
                if any(section in query_lower for section in ['section', 'paragraph', 'part', 'component']):
                    if any(question in query_lower for question in ['what', 'how', 'include', 'goes in']):
                        section_bonus = 0.2
                
                # Bonus for formatting + content questions
                format_content_bonus = 0
                if any(fmt in query_lower for fmt in ['phrase', 'format', 'structure']):
                    if any(doc in query_lower for doc in ['statement', 'section', 'paragraph']):
                        format_content_bonus = 0.25
                
                score += doc_creation_bonus + section_bonus + format_content_bonus
            
            # Normalize score
            intent_scores[intent_type] = min(score, 1.0)
        
        # Determine primary intent
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        # Calculate confidence based on score separation
        sorted_scores = sorted(intent_scores.values(), reverse=True)
        if len(sorted_scores) > 1:
            confidence = "high" if sorted_scores[0] - sorted_scores[1] >= 0.2 else "medium" if sorted_scores[0] >= 0.4 else "low"
        else:
            confidence = "high" if sorted_scores[0] >= 0.6 else "medium" if sorted_scores[0] >= 0.4 else "low"
        
        return {
            'primary_intent': primary_intent[0],
            'intent_scores': intent_scores,
            'confidence': confidence,
            'expanded_query': expanded_query,
            'military_terms_found': [term for term in self.military_terms.keys() if term in query_lower]
        }

    def determine_tool_strategy(self, query: str, intent_analysis: Dict) -> Dict[str, any]:
        """Determine enhanced tool usage strategy with better hybrid detection."""
        
        strategy_scores = {}
        reasoning_steps = []
        
        # Evaluate each strategy against its conditions
        for strategy_name, strategy_config in self.strategy_matrix.items():
            score = 0.0
            conditions_met = []
            
            if 'conditions' not in strategy_config:
                continue
                
            for condition_name, condition_func in strategy_config['conditions'].items():
                try:
                    if condition_name.endswith('_high') or condition_name.endswith('_low'):
                        # Score-based condition
                        if condition_func(intent_analysis['intent_scores']):
                            score += 0.25
                            conditions_met.append(condition_name)
                    else:
                        # Query-based condition
                        if condition_func(query):
                            score += 0.25
                            conditions_met.append(condition_name)
                except Exception as e:
                    # Handle any condition evaluation errors gracefully
                    print(f"Error evaluating condition {condition_name}: {e}")
            
            # Apply confidence boost
            if score > 0 and 'confidence_boost' in strategy_config:
                score += strategy_config['confidence_boost']
            
            strategy_scores[strategy_name] = min(score, 1.0)
            
            if conditions_met:
                reasoning_steps.append(f"{strategy_name}: {len(conditions_met)} conditions met - {', '.join(conditions_met)}")
        
        # Determine primary strategy
        primary_strategy = max(strategy_scores.items(), key=lambda x: x[1])
        
        # Map strategy to tools
        tool_mapping = {
            'csv_only': {'primary': 'csv', 'secondary': None},
            'pdf_only': {'primary': 'pdf', 'secondary': None},
            'hybrid_approach': {'primary': 'csv', 'secondary': 'pdf'},
            'clarification_required': {'primary': 'clarification', 'secondary': None}
        }
        
        tools = tool_mapping[primary_strategy[0]]
        
        return {
            'strategy': primary_strategy[0],
            'strategy_confidence': primary_strategy[1],
            'primary_tool': tools['primary'],
            'secondary_tool': tools['secondary'],
            'strategy_scores': strategy_scores,
            'reasoning_steps': reasoning_steps,
            'prompt_strategy': self.strategy_matrix[primary_strategy[0]]['prompt_strategy']
        }

    def enhanced_csv_search(self, query: str, intent_analysis: Dict, max_results: int = 5) -> List[Dict]:
        """Enhanced CSV search with intent-aware filtering and scoring."""
        
        # Extract key terms for better matching
        search_terms = []
        
        # Add original query terms
        search_terms.extend(query.lower().split())
        
        # Add military terms found in the query
        search_terms.extend(intent_analysis.get('military_terms_found', []))
        
        # Add intent-specific terms
        if intent_analysis['primary_intent'] == 'document_generation':
            search_terms.extend(['award', 'bullet', 'evaluation', 'citation'])
        
        # Perform multi-term search
        all_results = []
        
        for term in search_terms:
            # Try exact search first
            exact_results = self.csv_processor.search_exact(term)
            for result in exact_results:
                result['search_term'] = term
                result['match_type'] = 'exact'
                result['relevance_score'] = 1.0
            all_results.extend(exact_results)
            
            # Try fuzzy search with lower threshold
            fuzzy_results = self.csv_processor.search_fuzzy(term, threshold=0.3)
            for result in fuzzy_results:
                result['search_term'] = term
                result['match_type'] = 'fuzzy'
                result['relevance_score'] = result.get('similarity_score', 0.5)
            all_results.extend(fuzzy_results)
        
        # Remove duplicates and score
        seen = set()
        unique_results = []
        
        for result in all_results:
            key = f"{result.get('template_name', '')}-{result.get('field_label', '')}"
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # Sort by relevance score
        unique_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return unique_results[:max_results]

    def enhanced_pdf_search(self, query: str, intent_analysis: Dict, max_results: int = 5) -> List[Dict]:
        """Enhanced PDF search with expanded military terminology."""
        
        # Use expanded query for better semantic matching
        search_query = intent_analysis.get('expanded_query', query)
        print(f"DEBUG: PDF search query: '{search_query}'")
        
        # Debug ChromaDB collection
        try:
            collection = self.embedding_manager.get_collection("pdf_documents")
            count = collection.count()
            print(f"DEBUG: ChromaDB collection 'pdf_documents' has {count} documents")
            
        except Exception as e:
            print(f"DEBUG: ChromaDB collection test failed: {e}")
        
        try:
            results = self.embedding_manager.query_similar(
                collection_name="pdf_documents",
                query=search_query,
                n_results=max_results * 2  # Get more results for filtering
            )
            print(f"DEBUG: Raw PDF results from ChromaDB: {len(results)}")
            
            if not results:
                print("DEBUG: No results returned from ChromaDB")
                # Try with original query
                results = self.embedding_manager.query_similar(
                    collection_name="pdf_documents",
                    query=query,
                    n_results=max_results * 2
                )
                print(f"DEBUG: Original query '{query}' returned {len(results)} results")
                
                if not results:
                    return []
            
            # Score and filter results based on intent
            scored_results = []
            
            for i, result in enumerate(results):
                print(f"DEBUG: Processing result {i}: {result.keys()}")
                relevance_score = 1.0 - result.get('distance', 0.0)  # Convert distance to similarity
                
                # Boost score if military terms are present in the result
                text_lower = result.get('text', '').lower()
                military_term_matches = [term for term in intent_analysis.get('military_terms_found', []) 
                                       if term in text_lower]
                
                if military_term_matches:
                    relevance_score += len(military_term_matches) * 0.1
                
                # Boost score based on intent alignment
                if intent_analysis['primary_intent'] == 'information_retrieval':
                    if any(word in text_lower for word in ['process', 'procedure', 'step', 'role', 'responsibility']):
                        relevance_score += 0.2
                
                result['relevance_score'] = min(relevance_score, 1.0)
                result['military_terms_matched'] = military_term_matches
                scored_results.append(result)
                print(f"DEBUG: Result {i} score: {relevance_score:.3f}, text preview: {result.get('text', '')[:100]}...")
            
            # Sort by relevance and return top results
            scored_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            final_results = scored_results[:max_results]
            print(f"DEBUG: Returning {len(final_results)} final PDF results")
            return final_results
            
        except Exception as e:
            print(f"DEBUG: Error in enhanced PDF search: {str(e)}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")
            return []

    def generate_enhanced_response(self, query: str, csv_results: List[Dict], pdf_results: List[Dict], 
                                 intent_analysis: Dict, strategy: Dict) -> Dict:
        """Generate response using advanced prompt engineering strategies."""
        
        # Handle clarification requests
        if strategy['primary_tool'] == 'clarification':
            return self._generate_clarification_request(query, intent_analysis)
        
        # Build enhanced context
        context_parts = []
        
        if csv_results:
            context_parts.append("=== DOCUMENT TEMPLATES AND FORMATS ===")
            for result in csv_results:
                relevance_info = f" (Relevance: {result.get('relevance_score', 'N/A')}, Match: {result.get('match_type', 'N/A')})"
                context_parts.append(
                    f"Template: {result.get('template_name', 'Unknown')}\n"
                    f"Field: {result.get('field_label', 'Unknown')}\n"
                    f"Instructions: {result.get('instructions', 'No instructions')}{relevance_info}\n"
                )
        
        if pdf_results:
            context_parts.append("=== MILITARY KNOWLEDGE AND PROCEDURES ===")
            for result in pdf_results:
                metadata = result.get('metadata', {})
                relevance_info = f" (Relevance: {result.get('relevance_score', 'N/A')})"
                military_terms = result.get('military_terms_matched', [])
                terms_info = f" [Military terms: {', '.join(military_terms)}]" if military_terms else ""
                
                context_parts.append(
                    f"Source: {metadata.get('source', 'Unknown')} (Page {metadata.get('page', 'Unknown')})\n"
                    f"Content: {result.get('text', '')}{relevance_info}{terms_info}\n"
                )
        
        context = "\n".join(context_parts)
        
        # Select prompt strategy based on determined approach
        prompt_strategy = strategy.get('prompt_strategy', 'knowledge_focused')
        system_prompt = self._get_system_prompt(prompt_strategy, intent_analysis, strategy)
        
        # Create user prompt with enhanced context
        user_prompt = self._create_user_prompt(query, context, intent_analysis, strategy)
        
        # Generate response
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.llm.invoke(messages)
            return {
                "answer": response.content,
                "sources_used": {
                    "csv_sources": len(csv_results),
                    "pdf_sources": len(pdf_results)
                },
                "tool_used": strategy['primary_tool'],
                "confidence": strategy['strategy_confidence'],
                "intent_analysis": intent_analysis,
                "strategy": strategy,
                "reasoning_chain": {
                    "military_terms_expanded": len(intent_analysis.get('military_terms_found', [])),
                    "intent_confidence": intent_analysis['confidence'],
                    "strategy_reasoning": strategy['reasoning_steps'],
                    "context_sources": len(csv_results) + len(pdf_results)
                }
            }
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error generating a response: {str(e)}",
                "sources_used": {"csv_sources": 0, "pdf_sources": 0},
                "tool_used": "error",
                "confidence": "none",
                "intent_analysis": intent_analysis,
                "strategy": strategy,
                "reasoning_chain": {"error": str(e)}
            }

    def _get_system_prompt(self, strategy: str, intent_analysis: Dict, strategy_info: Dict) -> str:
        """Generate sophisticated system prompts based on strategy."""
        
        base_context = f"""You are an expert Army assistant with deep knowledge of Army procedures, forms, and operations. 
You have access to Army document templates and Army procedural knowledge to provide accurate, professional assistance.

IMPORTANT: Your knowledge and templates are specifically focused on the U.S. Army. If users ask about other military branches (Navy, Air Force, Marines, Space Force), politely explain that your expertise is Army-specific and suggest they consult resources specific to those branches.

Current Analysis:
- Primary Intent: {intent_analysis['primary_intent']}
- Intent Confidence: {intent_analysis['confidence']}
- Strategy: {strategy}
- Military Terms Identified: {', '.join(intent_analysis.get('military_terms_found', []))}
"""
        
        if strategy == 'template_focused':
            return base_context + """
TASK: Army Document Generation and Template Application

Your primary role is to create Army documents using proper Army formats and templates. You should:

1. **Follow Template Instructions Exactly**: Use the provided Army template format instructions precisely
2. **Use Appropriate Army Language**: Employ proper Army terminology, abbreviations, and writing style
3. **Be Concise and Professional**: Army documents should be clear, direct, and professional
4. **Include Relevant Details**: Incorporate specific achievements, dates, and quantifiable results when applicable
5. **Maintain Proper Formatting**: Follow Army writing standards and document structure
6. **Stay Army-Focused**: Only create documents for Army contexts using Army templates

Focus on creating documents that would meet Army standards and be suitable for official Army use. If asked about other service branches, politely redirect to Army-specific assistance.
"""
        
        elif strategy == 'knowledge_focused':
            return base_context + """
TASK: Army Knowledge and Information Retrieval

Your primary role is to provide accurate information about Army procedures, roles, and operations. You should:

1. **Provide Comprehensive Army Information**: Give detailed explanations of Army processes and procedures
2. **Use Authoritative Army Sources**: Base responses on official Army doctrine and established procedures
3. **Explain Army Context and Purpose**: Help users understand not just what to do, but why it's done that way in the Army
4. **Use Proper Army Terminology**: Employ correct Army terms and acronyms with explanations when needed
5. **Structure Information Logically**: Present Army information in a clear, organized manner
6. **Acknowledge Limitations**: If asked about other service branches, clearly state your expertise is Army-specific

Focus on being an authoritative source of Army knowledge while being honest about the scope of your expertise.
"""
        
        elif strategy == 'hybrid_reasoning':
            return base_context + """
TASK: Hybrid Army Document Generation with Contextual Knowledge

Your role combines Army document creation with deep Army knowledge application. You should:

1. **Integrate Multiple Army Sources**: Combine Army template formats with relevant Army knowledge and context
2. **Apply Army Situational Awareness**: Consider the specific Army context, unit type, and operational environment
3. **Enhance with Army Professional Knowledge**: Use Army expertise to improve basic templates with relevant details
4. **Maintain Army Document Standards**: Ensure all generated content meets Army formatting and professional standards
5. **Provide Comprehensive Army Solutions**: Create documents that are both formally correct and tactically sound for Army use
6. **Stay Within Army Scope**: Only provide assistance for Army-related requests

This is advanced Army document creation that requires both technical formatting skills and deep Army operational knowledge. When creating documents:
- Start with the doctrinal foundation from Army manuals and publications
- Apply the specific formatting requirements from templates
- Ensure the content is tactically and technically sound
- Use proper Army terminology and structure throughout
"""
        
        else:  # clarification strategy
            return base_context + """
TASK: Clarification and Guidance for Army Assistance

Your role is to help users clarify their Army-related requests and guide them toward more specific questions. You should:

1. **Ask Targeted Army Questions**: Help users specify what type of Army document or information they need
2. **Provide Army Examples**: Offer concrete examples of Army assistance you can provide
3. **Suggest Army Alternatives**: If the request is unclear, suggest related Army topics or documents
4. **Be Helpful and Patient**: Guide users to ask more specific Army-related questions that will get better results
5. **Explain Army Capabilities**: Help users understand what types of Army assistance are available
6. **Be Honest About Scope**: If asked about other service branches, clearly explain your Army focus

Focus on being a helpful guide that leads users to more productive Army-focused interactions.
"""

    def _create_user_prompt(self, query: str, context: str, intent_analysis: Dict, strategy: Dict) -> str:
        """Create enhanced user prompts with context and strategy information."""
        
        prompt_parts = []
        
        # Add strategy-specific context
        if strategy['primary_tool'] == 'csv' and strategy.get('secondary_tool') == 'pdf':
            prompt_parts.append("This is a hybrid request requiring both template information and military knowledge.")
            prompt_parts.append("IMPORTANT: Combine doctrinal knowledge from military manuals with specific formatting requirements from templates.")
        elif strategy['primary_tool'] == 'csv':
            prompt_parts.append("This is primarily a document generation request requiring template formatting.")
        elif strategy['primary_tool'] == 'pdf':
            prompt_parts.append("This is primarily an information retrieval request about military knowledge.")
        
        # Add military context if terms were found
        if intent_analysis.get('military_terms_found'):
            terms_list = ', '.join(intent_analysis['military_terms_found'])
            prompt_parts.append(f"Military terminology identified: {terms_list}")
        
        # Add confidence and strategy information
        prompt_parts.append(f"Analysis confidence: {intent_analysis['confidence']}")
        prompt_parts.append(f"Strategy confidence: {strategy['strategy_confidence']:.2f}")
        
        # Add the main context
        if context.strip():
            prompt_parts.append(f"\nAvailable Context and Sources:\n{context}")
        else:
            prompt_parts.append("\nNo specific context sources found. Please provide a general response based on standard military knowledge.")
        
        # Add the user's original query
        prompt_parts.append(f"\nUser Request: {query}")
        
        # Add strategy-specific instructions
        if strategy['primary_tool'] == 'csv':
            prompt_parts.append("\nFocus on using the template information to create properly formatted military documents.")
        elif strategy['primary_tool'] == 'pdf':
            prompt_parts.append("\nFocus on providing accurate information from military knowledge sources.")
        elif strategy.get('secondary_tool'):
            prompt_parts.append("\nCombine template formatting requirements with relevant military doctrine for a comprehensive response.")
            prompt_parts.append("Use the PDF sources for doctrinal foundation and the CSV sources for proper formatting and structure.")
        
        return "\n".join(prompt_parts)

    def _generate_clarification_request(self, query: str, intent_analysis: Dict) -> Dict:
        """Generate intelligent clarification requests based on analysis."""
        
        # Start with a friendly, conversational greeting
        clarification_parts = [
            f"Hi there! I'd be happy to help you with '{query}'"
        ]
        
        # Analyze what type of clarification is needed
        scores = intent_analysis['intent_scores']
        
        if scores.get('document_generation', 0) > 0.3 and scores.get('information_retrieval', 0) > 0.3:
            clarification_parts.append(
                "\nI can help you in a couple of ways. Are you looking to:"
                "\n• **Create a military document** (like an award citation, evaluation, or memo)?"
                "\n• **Get information** about military procedures or processes?"
                "\n• **Both** - maybe you need info to help write something?"
                "\n\nJust let me know what you're working on!"
            )
        elif scores.get('document_generation', 0) > 0.2:
            clarification_parts.append(
                "\nIt sounds like you might need help creating a document! I can help with things like:"
                "\n• Award bullets and citations"
                "\n• NCO/Officer evaluations" 
                "\n• Military memos and reports"
                "\n• DA forms and templates"
                "\n\nWhat kind of document are you working on?"
            )
        elif scores.get('information_retrieval', 0) > 0.2:
            clarification_parts.append(
                "\nI'm here to answer your military questions! I can explain things like:"
                "\n• Military processes and procedures"
                "\n• Staff roles and responsibilities"
                "\n• Training and operational guidance"
                "\n• Army regulations and standards"
                "\n\nWhat would you like to know about?"
            )
        else:
            clarification_parts.append(
                "\nI'm your military assistant and I can help with two main things:"
                "\n\n**📝 Creating Documents**"
                "\n• Award bullets and citations"
                "\n• Performance evaluations" 
                "\n• Military reports and memos"
                "\n\n**📚 Military Knowledge**"
                "\n• Procedures like MDMP"
                "\n• Staff roles (S1, S2, S3, etc.)"
                "\n• Training and operations"
                "\n\nWhat can I help you with today?"
            )
        
        # Add examples based on military terms found
        if intent_analysis.get('military_terms_found'):
            terms = intent_analysis['military_terms_found']
            clarification_parts.append(f"\nI noticed you mentioned: {', '.join(terms)}. That helps me understand the context!")
        
        # Add friendly examples
        clarification_parts.append(
            "\n**Here are some examples of what you can ask:**"
            "\n• *\"Write an award bullet for a Soldier who scored 580 on the ACFT\"*"
            "\n• *\"What does the S6 do during MDMP?\"*"
            "\n• *\"Help me write a situation paragraph for our NTC rotation\"*"
            "\n\nDon't worry about getting the wording perfect - just tell me what you need! 😊"
        )
        
        return {
            "answer": "\n".join(clarification_parts),
            "sources_used": {"csv_sources": 0, "pdf_sources": 0},
            "tool_used": "clarification",
            "confidence": "high",
            "intent_analysis": intent_analysis,
            "strategy": {"primary_tool": "clarification", "reasoning": "Friendly guidance needed"},
            "reasoning_chain": {
                "clarification_type": "conversational_guidance",
                "intent_scores": scores,
                "military_terms_found": intent_analysis.get('military_terms_found', [])
            }
        }

    def process_query(self, query: str) -> Dict:
        """Main enhanced query processing with advanced reasoning pipeline."""
        
        # Step 1: Advanced Intent Analysis
        intent_analysis = self.analyze_query_intent(query)
        
        # Step 2: Sophisticated Strategy Determination
        strategy = self.determine_tool_strategy(query, intent_analysis)
        
        # Step 3: Enhanced Source Retrieval
        csv_results = []
        pdf_results = []
        
        if strategy['primary_tool'] == 'csv' or strategy.get('secondary_tool') == 'csv':
            csv_results = self.enhanced_csv_search(query, intent_analysis)
            print(f"DEBUG: Found {len(csv_results)} CSV results")
        
        if strategy['primary_tool'] == 'pdf' or strategy.get('secondary_tool') == 'pdf':
            pdf_results = self.enhanced_pdf_search(query, intent_analysis)
            print(f"DEBUG: Found {len(pdf_results)} PDF results")
            for i, result in enumerate(pdf_results[:2]):  # Show first 2 results
                print(f"DEBUG: PDF result {i}: Page {result.get('metadata', {}).get('page')}, Text: {result.get('text', '')[:100]}...")
        
        print(f"DEBUG: Strategy - Primary: {strategy['primary_tool']}, Secondary: {strategy.get('secondary_tool')}")
        print(f"DEBUG: Intent scores: {intent_analysis['intent_scores']}")
        
        # Step 4: Advanced Response Generation
        response = self.generate_enhanced_response(
            query, csv_results, pdf_results, intent_analysis, strategy
        )
        
        # Step 5: Add Enhanced Metadata
        response.update({
            "classification": {
                "primary_intent": intent_analysis['primary_intent'],
                "confidence": intent_analysis['confidence'],
                "reasoning": f"Identified as {intent_analysis['primary_intent']} with {intent_analysis['confidence']} confidence. Strategy: {strategy['strategy']}"
            },
            "sources": {
                "csv_results": [
                    {
                        "template_name": r.get("template_name", ""),
                        "field_label": r.get("field_label", ""),
                        "instructions": r.get("instructions", "")[:200] + "..." if len(r.get("instructions", "")) > 200 else r.get("instructions", ""),
                        "relevance_score": r.get("relevance_score"),
                        "match_type": r.get("match_type")
                    }
                    for r in csv_results
                ],
                "pdf_results": [
                    {
                        "text": r.get("text", "")[:200] + "..." if len(r.get("text", "")) > 200 else r.get("text", ""),
                        "page": r.get("metadata", {}).get("page"),
                        "source": r.get("metadata", {}).get("source"),
                        "relevance_score": r.get("relevance_score"),
                        "military_terms_matched": r.get("military_terms_matched", [])
                    }
                    for r in pdf_results
                ]
            },
            "sources_used": {
                "csv_sources": len(csv_results),
                "pdf_sources": len(pdf_results)
            },
            "enhanced_metadata": {
                "military_terms_expanded": len(intent_analysis.get('military_terms_found', [])),
                "strategy_confidence": strategy['strategy_confidence'],
                "total_sources": len(csv_results) + len(pdf_results),
                "processing_pipeline": "enhanced_v3.0_hybrid_optimized"
            }
        })
        
        return response

# Maintain backward compatibility by creating an alias
class RAGAgent(EnhancedRAGAgent):
    """Backward compatibility alias for the enhanced agent."""
    pass