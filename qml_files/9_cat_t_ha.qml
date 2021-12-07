<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.22.0-Białowieża" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" minScale="1e+08" maxScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal mode="0" enabled="0" fetchMode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option name="WMSBackgroundLayer" type="bool" value="false"/>
      <Option name="WMSPublishDataSourceUrl" type="bool" value="false"/>
      <Option name="embeddedWidgets/count" type="int" value="0"/>
      <Option name="identify/format" type="QString" value="Value"/>
    </Option>
  </customproperties>
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option name="name" type="QString" value=""/>
      <Option name="properties"/>
      <Option name="type" type="QString" value="collection"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling zoomedInResamplingMethod="nearestNeighbour" maxOversampling="2" enabled="false" zoomedOutResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer nodataColor="" classificationMin="-472.3543091" type="singlebandpseudocolor" band="1" classificationMax="39.6022987" alphaBand="-1" opacity="1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>MinMax</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader colorRampType="DISCRETE" minimumValue="-472.35430910000002" clip="0" maximumValue="39.602298699999999" labelPrecision="4" classificationMode="2">
          <colorramp name="[source]" type="gradient">
            <Option type="Map">
              <Option name="color1" type="QString" value="230,0,0,255"/>
              <Option name="color2" type="QString" value="0,77,168,255"/>
              <Option name="discrete" type="QString" value="0"/>
              <Option name="rampType" type="QString" value="gradient"/>
              <Option name="stops" type="QString" value="0.920692;230,0,0,255:0.921669;255,85,0,255:0.92245;255,211,127,255:0.922643;255,255,190,255:0.922647;255,255,255,255:0.922841;211,255,190,255:0.923622;152,230,0,255:0.924598;0,132,168,255"/>
            </Option>
            <prop v="230,0,0,255" k="color1"/>
            <prop v="0,77,168,255" k="color2"/>
            <prop v="0" k="discrete"/>
            <prop v="gradient" k="rampType"/>
            <prop v="0.920692;230,0,0,255:0.921669;255,85,0,255:0.92245;255,211,127,255:0.922643;255,255,190,255:0.922647;255,255,255,255:0.922841;211,255,190,255:0.923622;152,230,0,255:0.924598;0,132,168,255" k="stops"/>
          </colorramp>
          <item label="&lt; -10 [t/ha]" alpha="255" color="#e60000" value="-1"/>
          <item label="-10 ~ -5 [t/ha]" alpha="255" color="#ff5500" value="-0.5"/>
          <item label="-5 ~ -1 [t/ha]" alpha="255" color="#ffd37f" value="-0.1"/>
          <item label="-1 ~ -0,01 [t/ha]" alpha="255" color="#ffffbe" value="-0.001"/>
          <item label="-0,1 ~ 0,1 [t/ha]" alpha="255" color="#ffffff" value="0.001"/>
          <item label="0,1 ~ 1 [t/ha]" alpha="255" color="#d3ffbe" value="0.1"/>
          <item label="1 ~ 5 [t/ha]" alpha="255" color="#98e600" value="0.5"/>
          <item label="5 ~ 10 [t/ha]" alpha="255" color="#0084a8" value="1"/>
          <item label="> 10 [t/ha]" alpha="255" color="#004da8" value="inf"/>
          <rampLegendSettings useContinuousLegend="1" suffix="" minimumLabel="" maximumLabel="" prefix="" direction="0" orientation="2">
            <numericFormat id="basic">
              <Option type="Map">
                <Option name="decimal_separator" type="QChar" value=""/>
                <Option name="decimals" type="int" value="6"/>
                <Option name="rounding_type" type="int" value="0"/>
                <Option name="show_plus" type="bool" value="false"/>
                <Option name="show_thousand_separator" type="bool" value="true"/>
                <Option name="show_trailing_zeros" type="bool" value="false"/>
                <Option name="thousand_separator" type="QChar" value=""/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" gamma="1" contrast="0"/>
    <huesaturation colorizeGreen="128" grayscaleMode="0" colorizeStrength="100" colorizeBlue="128" colorizeOn="0" saturation="0" invertColors="0" colorizeRed="255"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
