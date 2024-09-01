import streamlit as st
from radixhopper import BaseConverter, ConversionInput, ConversionError

st.title("RadixHopper ✨")
st.write("Convert numbers between different bases (2-36). Cyclic fractions are displayed with an overline.")


num = st.text_input("Enter number to convert:", value="0")
base_from = st.number_input("Enter base to convert from:", min_value=2, max_value=36, value=10)
base_to = st.number_input("Enter base to convert to:", min_value=2, max_value=36, value=10)

if st.button("Convert"):
    try:
        input_data = ConversionInput(num=num, base_from=base_from, base_to=base_to)
        result = BaseConverter.base_convert(input_data)
        
        st.success("Conversion successful!")
        
        if '[' in result and ']' in result:
            parts = result.split('[')
            non_repeating = parts[0]
            repeating = parts[1].strip(']')
            formatted_result = f"Result: {non_repeating}<span style='text-decoration: overline;'>{repeating}</span>"
            st.markdown(formatted_result, unsafe_allow_html=True)
        else:
            st.markdown(f"Result: {result}")
    except ConversionError as e:
        st.error(f"Error: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")