cmake_minimum_required(VERSION 3.10.2)

project( ShrinkWrapLabelImage )

find_package( ITK REQUIRED )
include( ${ITK_USE_FILE} )

add_executable( ShrinkWrapLabelImage Code.cxx )
target_link_libraries( ShrinkWrapLabelImage ${ITK_LIBRARIES} )

install( TARGETS ShrinkWrapLabelImage
  DESTINATION bin/ITKSphinxExamples/Segmentation/LevelSets
  COMPONENT Runtime
)

install( FILES Code.cxx CMakeLists.txt Code.py
  DESTINATION share/ITKSphinxExamples/Code/Segmentation/LevelSets/ShrinkWrapLabelImage
  COMPONENT Code
)

enable_testing()

set(input_image ${CMAKE_CURRENT_BINARY_DIR}/cthead1.png)
set(output_image Output.png)
set(test_options)


add_test( NAME ShrinkWrapLabelImageTest
  COMMAND ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/ShrinkWrapLabelImage
  ${input_image}
  ${output_image}
  ${test_options}
)

if( ITK_WRAP_PYTHON )
  find_package(PythonInterp REQUIRED)
  string( REPLACE . "Python." output_image "${output_image}" )
  add_test( NAME ShrinkWrapLabelImageTestPython
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/Code.py
      ${input_image}
      ${output_image}
      ${test_options}
    )
endif()
