package ru.meta.wearos.classic1.fixtures;

import android.graphics.drawable.Icon;
import android.os.RemoteException;
import androidx.wear.watchface.complications.data.*;
import androidx.wear.watchface.complications.datasource.*;

/** Emulator-only fixture. Never packaged into the production watchface. */
public abstract class FixtureService extends ComplicationDataSourceService {
    protected abstract String title();
    protected abstract String value();
    private PlainComplicationText plain(String value) { return new PlainComplicationText.Builder(value).build(); }
    private ComplicationData data() {
        ShortTextComplicationData.Builder builder = new ShortTextComplicationData.Builder(plain(value()), plain("TEST DATA: " + title() + " " + value())).setTitle(plain(title()));
        if (this instanceof Weather) builder.setMonochromaticImage(new MonochromaticImage.Builder(Icon.createWithResource(this, R.drawable.rain)).build());
        return builder.build();
    }
    @Override public void onComplicationRequest(ComplicationRequest request, ComplicationRequestListener listener) {
        try { listener.onComplicationData(data()); } catch (RemoteException error) { throw new RuntimeException(error); }
    }
    @Override public ComplicationData getPreviewData(ComplicationType type) { return data(); }
    public static class Heart extends FixtureService { protected String title(){return "ПУЛЬС";} protected String value(){return "72";} }
    public static class Weather extends FixtureService { protected String title(){return "ПОГОДА";} protected String value(){return "+4°C";} }
    public static class Floors extends FixtureService { protected String title(){return "ЭТАЖИ";} protected String value(){return "9";} }
    public static class Battery extends FixtureService { protected String title(){return "ЗАРЯД";} protected String value(){return "82%";} }
    public static class Steps extends FixtureService { protected String title(){return "ШАГИ";} protected String value(){return "10 780";} }
}
