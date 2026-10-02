package org.emulationstation.frontend.auth;

final class StationProtocolPath {
    private StationProtocolPath() {}
    static String activationChallenge() { return "/v1/station/activations/challenge"; }
    static String activationComplete() { return "/v1/station/activations/complete"; }
    static String challenge() { return "/v1/station/challenges"; }
    static String session() { return "/v1/station/sessions"; }
    static String profile() { return "/v1/station/me"; }
    static String catalog() { return "/v1/station/catalog"; }
    static String cover(String coverId) { return "/v1/station/covers/" + coverId; }
    static String authorize() { return "/v1/station/downloads/authorize"; }
    static String artifact(String grantId) { return "/v1/station/artifacts/" + grantId; }
}
