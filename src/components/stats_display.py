import streamlit as st

def display_global_stats(analyzer):
    # Selector for game type
    game_type = st.selectbox(
        "Type de parties",
        ["Global", "Scrims", "Tournois"],
        key="global_stats_type"
    )
    
    # Get filtered stats based on selection
    if game_type == "Scrims":
        stats = analyzer.get_global_stats(filter_type="Scrim")
    elif game_type == "Tournois":
        stats = analyzer.get_global_stats(filter_type="Tournoi")
    else:
        stats = analyzer.get_global_stats()
    
    st.header("Statistiques générales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Winrate global", f"{stats['winrate']:.1f}%")
    with col2:
        st.metric("Parties jouées", stats['total_games'])
    with col3:
        st.metric("Victoires", stats['wins'])
    with col4:
        st.metric("Défaites", stats['losses']) 
    
    # Detailed blue/red side stats
    st.subheader("Statistiques par side")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Blue Side")
        st.metric("Winrate Blue Side", f"{stats['blue_side_winrate']:.1f}%")
        st.write(f"{stats['blue_side_wins']} Win - {stats['blue_side_games'] - stats['blue_side_wins']} Lose")
        
    with col2:
        st.write("Red Side")
        st.metric("Winrate Red Side", f"{stats['red_side_winrate']:.1f}%")
        st.write(f"{stats['red_side_wins']} Win - {stats['red_side_games'] - stats['red_side_wins']} Lose")